import streamlit as st
import json
import os
from datetime import datetime
from pathlib import Path

# תיקון נתיבי שמירה בטוחים (בתיקיית הבית למניעת שגיאות הרשאה)
HOME_DIR = Path.home()
DATA_FILE = HOME_DIR / "segel_dining_hall_menus.json"
BANK_FILE = HOME_DIR / "segel_dish_bank.json"

# פונקציות טעינה ושמירה לתפריט היומי
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# פונקציות טעינה ושמירה לבנק המנות (הזיכרון של האפליקציה)
def load_bank():
    if os.path.exists(BANK_FILE):
        with open(BANK_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_to_bank(category_key, name, products, instructions):
    if not name or name.strip() == "":
        return
    bank = load_bank()
    if category_key not in bank:
        bank[category_key] = {}
    
    # שמירת המנה עם כל הפרודוקטים והוראות ההכנה שלה
    bank[category_key][name.strip()] = {
        "products": products,
        "instructions": instructions
    }
    with open(BANK_FILE, "w", encoding="utf-8") as f:
        json.dump(bank, f, ensure_ascii=False, indent=4)

# טעינת בסיסי הנתונים
menus_db = load_data()
dish_bank = load_bank()

# עיצוב בסיסי ליישור לימין
st.markdown("""
    <style>
    .reportview-container .main .block-container{ max-width: 1050px; }
    h1, h2, h3, p, label, div, span { direction: rtl; text-align: right; }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stNumberInput>div>div>input { text-align: right; direction: rtl; }
    div[data-baseweb="select"] { direction: rtl; text-align: right; }
    .report-box { background-color: #f0f2f6; padding: 20px; border-radius: 10px; border-right: 5px solid #ff4b4b; margin-top: 25px; }
    </style>
""", unsafe_allow_html=True)

st.title("⭐ מערכת חדר אוכל סגל - עם זיכרון מנות")
st.write("הקלד מנה חדשה או בחר מתוך מנות קיימות שנשמרו בעבר כדי למלא פרודוקטים אוטומטית")

# בחירת תאריך
selected_date = st.date_input("בחר תאריך לתפריט:", datetime.today()).strftime("%Y-%m-%d")

meals = ["ארוחת בוקר", "ארוחת צהריים", "ארוחת ערב"]
current_menu = menus_db.get(selected_date, {})
updated_menu = {}

# פונקציה לייצור פריט מזון חכם עם זיכרון מהבנק
def render_food_item(meal_data, meal_name, category_key, item_label, item_index):
    category_data = meal_data.get(category_key, [])
    while len(category_data) <= item_index:
        category_data.append({"name": "", "item_diners": 40, "products": [], "instructions": ""})
        
    existing_item = category_data[item_index]
    
    # שליפת מנות שכבר קיימות בבנק עבור קטגוריה זו (למשל סלטים או עיקריות)
    existing_bank_dishes = list(dish_bank.get(category_key, {}).keys())
    
    # הכנת רשימת האפשרויות לבחירה: "חדש/הקלדה חופשית" או המנות מהבנק
    select_options = ["➕ הקלד מנה חדשה בתיבה למטה..."] + existing_bank_dishes
    
    # קביעת ברירת המחדל של תיבת הבחירה
    saved_name = existing_item.get("name", "")
    default_index = 0
    if saved_name in existing_bank_dishes:
        default_index = select_options.index(saved_name)
    
    # 1. תיבת בחירה ממנות עבר
    selected_from_box = st.selectbox(
        f"בחר {item_label} מוכן (או הקלד חדש):",
        options=select_options,
        index=default_index,
        key=f"{selected_date}_{meal_name}_{category_key}_select_{item_index}"
    )
    
    # 2. שדה קלט טקסט - מופעל אם בחרו "הקלד מנה חדשה" או מציג את הבחירה
    if selected_from_box == "➕ הקלד מנה חדשה בתיבה למטה...":
        name = st.text_input(f"שם ה{item_label} החדש:", value="", key=f"{selected_date}_{meal_name}_{category_key}_name_{item_index}", placeholder="למשל: סלט כרוב אסיאתי")
    else:
        name = selected_from_box
        st.info(f"📋 נבחרה מנה מוכנה: **{name}** (הפרודוקטים וההוראות נטענו בהצלחה)")

    updated_products = []
    instructions = ""
    item_diners = existing_item.get("item_diners", 40)
    
    if name:
        # בדיקה האם המנה קיימת בבנק כדי למשוך את הפרודוקטים שלה כברירת מחדל
        bank_dish_data = dish_bank.get(category_key, {}).get(name, {})
        
        with st.expander(f"📝 פרודוקטים ומחשבון כמויות עבור: {name}"):
            
            item_diners = st.number_input(
                f"👥 כמה סועדי סגל יאכלו מנת '{name}'?", 
                min_value=1, 
                value=int(existing_item.get("item_diners", 40)), 
                step=5,
                key=f"{selected_date}_{meal_name}_{category_key}_{item_index}_diners"
            )
            
            st.markdown("---")
            st.markdown("**🍎 רשימת פרודוקטים וצורת הכנה:**")
            
            # קביעה מאיפה לקחת את הפרודוקטים: מהתפריט השמור של היום, או מבנק המנות הכללי
            if existing_item.get("name") == name:
                source_products = existing_item.get("products", [])
            else:
                source_products = bank_dish_data.get("products", [])
                
            col_p_name, col_p_action, col_p_grams, col_p_total = st.columns([3, 2.5, 2, 2])
            with col_p_name: st.caption("שם הפרודוקט")
            with col_p_action: st.caption("מה לעשות עם המוצר?")
            with col_p_grams: st.caption("גרם לאיש סגל")
            with col_p_total: st.caption("סך הכל דרוש")

            action_options = ["➖ ללא פעולה", "🔪 לחתוך", "🥔 לקלף", "🧼 לשטוף בלבד", "🔄 לקלף ולחתוך"]

            for p_idx in range(4):
                p_data = source_products[p_idx] if p_idx < len(source_products) else {"prod_name": "", "action": "➖ ללא פעולה", "grams_per_person": 0.0}
                
                c1, c2, c3, c4 = st.columns([3, 2.5, 2, 2])
                with c1:
                    p_name = st.text_input(f"מוצר {p_idx+1}", value=p_data.get("prod_name", ""), key=f"{selected_date}_{meal_name}_{category_key}_{item_index}_pname_{p_idx}", label_visibility="collapsed")
                with c2:
                    current_action = p_data.get("action", "➖ ללא פעולה")
                    if current_action not in action_options: current_action = "➖ ללא פעולה"
                    p_action = st.selectbox(f"פעולה {p_idx+1}", options=action_options, index=action_options.index(current_action), key=f"{selected_date}_{meal_name}_{category_key}_{item_index}_paction_{p_idx}", label_visibility="collapsed")
                with c3:
                    p_grams = st.number_input(f"גרם {p_idx+1}", min_value=0.0, value=float(p_data.get("grams_per_person", 0.0)), step=5.0, key=f"{selected_date}_{meal_name}_{category_key}_{item_index}_pgrams_{p_idx}", label_visibility="collapsed")
                with c4:
                    total_kg = (p_grams * item_diners) / 1000
                    st.markdown(f"<div style='padding-top:5px;'><b>{total_kg:,.2f} ק\"ג</b></div>", unsafe_allow_html=True)
                
                if p_name:
                    updated_products.append({
                        "prod_name": p_name, "action": p_action, "grams_per_person": p_grams, "total_kg": total_kg
                    })
            
            st.write("")
            
            # קביעת הערות הכנה
            if existing_item.get("name") == name:
                default_instructions = existing_item.get("instructions", "")
            else:
                default_instructions = bank_dish_data.get("instructions", "")
                
            instructions = st.text_area(
                "🥣 הוראות הכנה ועבודה למטבח:", 
                value=default_instructions, 
                key=f"{selected_date}_{meal_name}_{category_key}_inst_{item_index}"
            )
            
            # שמירה אוטומטית לבנק המנות ברגע שמקלידים או מעדכנים
            if len(updated_products) > 0:
                save_to_bank(category_key, name, updated_products, instructions)
            
    return {"name": name, "item_diners": item_diners, "products": updated_products, "instructions": instructions}

# בניית הטאבים
tabs = st.tabs(meals)

for count, meal_name in enumerate(meals):
    with tabs[count]:
        st.subheader(f"🍳 תפריט סגל ל-{meal_name}")
        meal_data = current_menu.get(meal_name, {})
        updated_menu[meal_name] = {}
        
        st.markdown("### 🥗 סלטים (5 סלטים)")
        salads_list = []
        for i in range(5):
            salads_list.append(render_food_item(meal_data, meal_name, "salads", f"סלט {i+1}", i))
        updated_menu[meal_name]["salads"] = salads_list
        
        st.divider()
        
        st.markdown("### 🍗 מנות עיקריות (3 מנות)")
        mains_list = []
        for i in range(3):
            mains_list.append(render_food_item(meal_data, meal_name, "mains", f"מנה עיקרית {i+1}", i))
        updated_menu[meal_name]["mains"] = mains_list

        st.divider()

        st.markdown("### 🍚 פחמימות (3 פחמימות)")
        carbs_list = []
        for i in range(3):
            carbs_list.append(render_food_item(meal_data, meal_name, "carb", f"פחמימה {i+1}", i))
        updated_menu[meal_name]["carb"] = carbs_list

        st.divider()

        st.markdown("### 🍰 קינוח סגל")
        updated_menu[meal_name]["dessert"] = [render_food_item(meal_data, meal_name, "dessert", "שם הקינוח", 0)]

st.divider()

# כפתורי שמירה ודוח
col_save, col_report = st.columns(2)
with col_save:
    if st.button("💾 שמור תפריט סגל ליום זה", use_container_width=True):
        menus_db[selected_date] = updated_menu
        save_data(menus_db)
        st.success(f"🎉 תפריט הסגל לתאריך {selected_date} נשמר, וכל המנות החדשות התווספו לבנק המנות!")

with col_report:
    show_report = st.button("📋 הפק תוכנית עבודה יומית למטבח", type="primary", use_container_width=True)

if show_report:
    st.markdown("<div class='report-box'>", unsafe_allow_html=True)
    st.header(f"📋 תוכנית עבודה מרוכזת למטבח הסגל - {selected_date}")
    aggregated_ingredients = {}
    
    for meal_key, meal_content in updated_menu.items():
        for cat_key, items_list in meal_content.items():
            for item in items_list:
                if item.get("name"):
                    for prod in item.get("products", []):
                        p_name = prod["prod_name"].strip()
                        p_action = prod["action"]
                        p_weight = prod["total_kg"]
                        
                        key = (p_name, p_action)
                        if key in aggregated_ingredients:
                            aggregated_ingredients[key] += p_weight
                        else:
                            aggregated_ingredients[key] = p_weight
                            
    if aggregated_ingredients:
        st.markdown("### 🛒 סך הכל פרודוקטים שיש להוציא מהמחסן ולעבד:")
        report_data = []
        for (p_name, p_action), total_weight in aggregated_ingredients.items():
            report_data.append({
                "פרודוקט": p_name, "פעולה נדרשת": p_action, "משקל כולל (ק\"ג)": f"{total_weight:,.2f} ק\"ג"
            })
        st.table(report_data)
    else:
        st.warning("לא נמצאו פרודוקטים רשומים ביום זה.")
    st.markdown("</div>", unsafe_allow_html=True)
