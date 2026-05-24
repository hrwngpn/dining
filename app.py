import streamlit as st
import json
import os
from datetime import datetime
from pathlib import Path

# תיקון נתיבי שמירה בטוחים (בתיקיית הבית למניעת שגיאות הרשאה)
HOME_DIR = Path.home()
DATA_FILE = HOME_DIR / "segel_dining_hall_menus.json"
BANK_FILE = HOME_DIR / "segel_dish_bank.json"

# תפריט בסיס מוכן מראש למטבח הסגל (מוזן אוטומטית אם הבנק ריק)
DEFAULT_BANK = {
    "salads": {
        "סלט ירקות ישראלי": {
            "products": [
                {"prod_name": "עגבנייה", "action": "🔪 לחתוך", "grams_per_person": 50.0},
                {"prod_name": "מלפפון", "action": "🔪 לחתוך", "grams_per_person": 50.0},
                {"prod_name": "בצל סגול", "action": "🔄 לקלף ולחתוך", "grams_per_person": 15.0},
                {"prod_name": "פטרוזיליה", "action": "🧼 לשטוף בלבד", "grams_per_person": 5.0}
            ],
            "instructions": "לחתוך את הירקות לקוביות קטנות ואחידות. לתבל בשמן זית, מיץ לימון טרי ומלח ממש לפני ההגשה כדי למנוע נוזלים."
        },
        "סלט כרוב וגזר במיונז": {
            "products": [
                {"prod_name": "כרוב לבן", "action": "🔪 לחתוך", "grams_per_person": 60.0},
                {"prod_name": "גזר", "action": "🔄 לקלף ולחתוך", "grams_per_person": 20.0},
                {"prod_name": "מיונז", "action": "➖ ללא פעולה", "grams_per_person": 15.0}
            ],
            "instructions": "לקצוץ את הכרוב דק, לגרד את הגזר בפומפייה. לערבב היטב עם מיונז, קורט סוכר, מלח ומעט חומץ. להשהות שעה במקרר לספיגת טעמים."
        },
        "סלט חסה וקרוטונים": {
            "products": [
                {"prod_name": "חסה ערבית", "action": "🧼 לשטוף בלבד", "grams_per_person": 50.0},
                {"prod_name": "קרוטונים", "action": "➖ ללא פעולה", "grams_per_person": 15.0},
                {"prod_name": "רוטב שום", "action": "➖ ללא פעולה", "grams_per_person": 20.0}
            ],
            "instructions": "לשטוף ולייבש את החסה היטב, לקרוע לחתיכות בינוניות. להוסיף את הקרוטונים והרוטב ממש דקה לפני הגשת הסגל."
        },
        "סלט חומוס ביתי": {
            "products": [
                {"prod_name": "גרגרי חומוס מבושלים", "action": "🧼 לשטוף בלבד", "grams_per_person": 60.0},
                {"prod_name": "טחינה גולמית", "action": "➖ ללא פעולה", "grams_per_person": 20.0},
                {"prod_name": "שום כתוש", "action": "🥔 לקלף", "grams_per_person": 2.0}
            ],
            "instructions": "לטחון את גרגרי החומוס החמים עם הטחינה, השום, מיץ לימון ומים קרים עד לקבלת מרקם חלק. להגיש עם זילוף שמן זית ופפריקה."
        },
        "סלט טחינה ירוקה": {
            "products": [
                {"prod_name": "טחינה גולמית", "action": "➖ ללא פעולה", "grams_per_person": 40.0},
                {"prod_name": "פטרוזיליה וכלוסברה", "action": "🧼 לשטוף בלבד", "grams_per_person": 10.0},
                {"prod_name": "מיץ לימון", "action": "➖ ללא פעולה", "grams_per_person": 15.0}
            ],
            "instructions": "לערבב טחינה עם מים קרים ולימון. לטחון פנימה את עשבי התיבול לקבלת צבע ירוק בוהק."
        }
    },
    "mains": {
        "כרעי עוף בתנור עם פפריקה": {
            "products": [
                {"prod_name": "כרעי עוף טרי", "action": "🧼 לשטוף בלבד", "grams_per_person": 250.0},
                {"prod_name": "שמן קנולה", "action": "➖ ללא פעולה", "grams_per_person": 10.0},
                {"prod_name": "תבלין פפריקה וגריל", "action": "➖ ללא פעולה", "grams_per_person": 5.0}
            ],
            "instructions": "לערבב את השמן עם התבלינים, לעסות את העוף היטב. לסדר בתבניות עמוקות, לכסות בנייר כסף ולאפות שעה ב-180 מעלות. להסיר כיסוי ל-20 דקות נוספות להשחמה."
        },
        "קציצות בקר ברוטב עגבניות": {
            "products": [
                {"prod_name": "בשר בקר טחון", "action": "➖ ללא פעולה", "grams_per_person": 160.0},
                {"prod_name": "רוטב עגבניות מוכן", "action": "➖ ללא פעולה", "grams_per_person": 80.0},
                {"prod_name": "בצל וירק לקציצות", "action": "🔄 לקלף ולחתוך", "grams_per_person": 25.0}
            ],
            "instructions": "לערבב את הבשר עם הבצל והירק הקצוצים, ליצור קציצות אחידות. לבשל בתוך רוטב עגבניות מבעבע על אש קטנה במשך כ-40 דקות."
        },
        "פילה אמנון בעשבי תיבול": {
            "products": [
                {"prod_name": "דג פילה אמנון", "action": "🧼 לשטוף בלבד", "grams_per_person": 150.0},
                {"prod_name": "שמן זית", "action": "➖ ללא פעולה", "grams_per_person": 8.0},
                {"prod_name": "שום וכוסברה קצוצה", "action": "🔄 לקלף ולחתוך", "grams_per_person": 12.0}
            ],
            "instructions": "למרוח את הדגים בשמן זית, שום כתוש וכוסברה. לאפות בתנור חם מאוד (200 מעלות) במשך 12-15 דקות בלבד שלא יתייבש."
        }
    },
    "carb": {
        "אורז לבן אחד-אחד": {
            "products": [
                {"prod_name": "אורז פרסי/יסמין", "action": "🧼 לשטוף בלבד", "grams_per_person": 70.0},
                {"prod_name": "שמן קנולה", "action": "➖ ללא פעולה", "grams_per_person": 8.0}
            ],
            "instructions": "לטגן את האורז בשמן כ-3 דקות, להוסיף מים רותחים (ביחס של 1.5 כוסות מים על כל כוס אורז) ומלח. לבשל על אש קטנה בסיר מכוסה 18 דקות, להשאיר סגור עוד 10 דקות."
        },
        "תפוחי אדמה אפויים (סירות)": {
            "products": [
                {"prod_name": "תפוח אדמה", "action": "🔄 לקלף ולחתוך", "grams_per_person": 180.0},
                {"prod_name": "שמן ומלח גס", "action": "➖ ללא פעולה", "grams_per_person": 10.0}
            ],
            "instructions": "לחתוך את תפוחי האדמה לפלחים (סירות), לערבב עם שמן, מלח גס ומעט רוזמרין. לאפות ב-200 מעלות עד שרך מבפנים וקריספי מבחוץ."
        },
        "פתיתים עם בצל מטוגן": {
            "products": [
                {"prod_name": "פתיתים אפויים", "action": "➖ ללא פעולה", "grams_per_person": 70.0},
                {"prod_name": "בצל", "action": "🔄 לקלף ולחתוך", "grams_per_person": 20.0}
            ],
            "instructions": "לטגן את הבצל הקצוץ עד להזהבה עמוקה. להוסיף את הפתיתים, לטגן דקה, להוסיף מים רותחים ולבשל לפי הוראות היצרן."
        }
    },
    "dessert": {
        "סלט פירות העונה": {
            "products": [
                {"prod_name": "פירות מעורבים (תפוח, תפוז, בננה)", "action": "🔄 לקלף ולחתוך", "grams_per_person": 100.0}
            ],
            "instructions": "לחתוך את כל הפירות לקוביות קטנות, לערבב עם מעט מיץ תפוזים טבעי וסוכר וניל. להגיש קר בקעריות אישיות לסגל."
        }
    }
}

# פונקציות טעינה ושמירה
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_bank():
    # אם הקובץ לא קיים, נייצר אותו אוטומטית עם תפריט הבסיס המוכן
    if not os.path.exists(BANK_FILE):
        with open(BANK_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_BANK, f, ensure_ascii=False, indent=4)
        return DEFAULT_BANK
    
    with open(BANK_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_to_bank(category_key, name, products, instructions):
    if not name or name.strip() == "":
        return
    bank = load_bank()
    if category_key not in bank:
        bank[category_key] = {}
    
    bank[category_key][name.strip()] = {
        "products": products,
        "instructions": instructions
    }
    with open(BANK_FILE, "w", encoding="utf-8") as f:
        json.dump(bank, f, ensure_ascii=False, indent=4)

# טעינת המידע
menus_db = load_data()
dish_bank = load_bank()

# עיצוב בסיסי בעברית
st.markdown("""
    <style>
    .reportview-container .main .block-container{ max-width: 1050px; }
    h1, h2, h3, p, label, div, span { direction: rtl; text-align: right; }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stNumberInput>div>div>input { text-align: right; direction: rtl; }
    div[data-baseweb="select"] { direction: rtl; text-align: right; }
    .report-box { background-color: #f0f2f6; padding: 20px; border-radius: 10px; border-right: 5px solid #ff4b4b; margin-top: 25px; }
    </style>
""", unsafe_allow_html=True)

st.title("⭐ מערכת חדר אוכל סגל - תפריט בסיס מוכן")
st.write("בחר מתוך רשימת המנות המוכנות מראש, או הקלד מנה חדשה כדי להוסיף אותה לבנק")

# בחירת תאריך
selected_date = st.date_input("בחר תאריך לתפריט:", datetime.today()).strftime("%Y-%m-%d")

meals = ["ארוחת בוקר", "ארוחת צהריים", "ארוחת ערב"]
current_menu = menus_db.get(selected_date, {})
updated_menu = {}

def render_food_item(meal_data, meal_name, category_key, item_label, item_index):
    category_data = meal_data.get(category_key, [])
    while len(category_data) <= item_index:
        category_data.append({"name": "", "item_diners": 40, "products": [], "instructions": ""})
        
    existing_item = category_data[item_index]
    existing_bank_dishes = list(dish_bank.get(category_key, {}).keys())
    
    select_options = ["➕ הקלד מנה חדשה בתיבה למטה..."] + existing_bank_dishes
    
    saved_name = existing_item.get("name", "")
    default_index = 0
    if saved_name in existing_bank_dishes:
        default_index = select_options.index(saved_name)
    
    selected_from_box = st.selectbox(
        f"בחר {item_label} מוכן (או הקלד חדש):",
        options=select_options,
        index=default_index,
        key=f"{selected_date}_{meal_name}_{category_key}_select_{item_index}"
    )
    
    if selected_from_box == "➕ הקלד מנה חדשה בתיבה למטה...":
        name = st.text_input(f"שם ה{item_label} החדש:", value="", key=f"{selected_date}_{meal_name}_{category_key}_name_{item_index}", placeholder="הקלד שם כאן...")
    else:
        name = selected_from_box
        st.info(f"📋 המנה **{name}** נטענה עם פרודוקטים מוכנים.")

    updated_products = []
    instructions = ""
    item_diners = existing_item.get("item_diners", 40)
    
    if name:
        bank_dish_data = dish_bank.get(category_key, {}).get(name, {})
        
        with st.expander(f"📝 פרודוקטים ומחשבון כמויות עבור: {name}"):
            item_diners = st.number_input(
                f"👥 כמה סועדי סגל יאכלו מנת '{name}'?", 
                min_value=1, value=int(existing_item.get("item_diners", 40)), step=5,
                key=f"{selected_date}_{meal_name}_{category_key}_{item_index}_diners"
            )
            
            st.markdown("---")
            st.markdown("**🍎 רשימת פרודוקטים וצורת הכנה:**")
            
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
            if existing_item.get("name") == name:
                default_instructions = existing_item.get("instructions", "")
            else:
                default_instructions = bank_dish_data.get("instructions", "")
                
            instructions = st.text_area("🥣 הוראות הכנה ועבודה למטבח:", value=default_instructions, key=f"{selected_date}_{meal_name}_{category_key}_inst_{item_index}")
            
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

# כפתורים
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
