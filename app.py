import streamlit as st
import json
import os
from datetime import datetime

# הגדרת שם הקובץ לשמירת הנתונים
DATA_FILE = "segel_dining_hall_menus.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

menus_db = load_data()

# עיצוב בסיסי ליישור לימין והתאמה לחדר אוכל סגל
st.markdown("""
    <style>
    .reportview-container .main .block-container{ max-width: 1050px; }
    h1, h2, h3, p, label, div, span { direction: rtl; text-align: right; }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stNumberInput>div>div>input { text-align: right; direction: rtl; }
    div[data-baseweb="select"] { direction: rtl; text-align: right; }
    .report-box { background-color: #f0f2f6; padding: 20px; border-radius: 10px; border-right: 5px solid #ff4b4b; margin-top: 25px; }
    </style>
""", unsafe_allow_html=True)

st.title("⭐ מערכת ניהול חדר אוכל סגל")
st.write("תפריט מורחב (5 סלטים, 3 עיקריות, 3 פחמימות, קינוח) כולל ריכוז כמויות ודפי עבודה למטבח")

# בחירת תאריך
selected_date = st.date_input("בחר תאריך לתפריט הסגל:", datetime.today()).strftime("%Y-%m-%d")

meals = ["ארוחת בוקר", "ארוחת צהריים", "ארוחת ערב"]
current_menu = menus_db.get(selected_date, {})
updated_menu = {}

# פונקציה לייצור פריט מזון עם מוצרים ופעולות הכנה
def render_food_item(meal_data, meal_name, category_key, item_label, item_index):
    category_data = meal_data.get(category_key, [])
    while len(category_data) <= item_index:
        category_data.append({"name": "", "item_diners": 40, "products": [], "instructions": ""})
        
    existing_item = category_data[item_index]
    
    # הזנת שם המנה
    name = st.text_input(f"{item_label}:", value=existing_item.get("name", ""), key=f"{selected_date}_{meal_name}_{category_key}_name_{item_index}")
    
    updated_products = []
    instructions = ""
    item_diners = existing_item.get("item_diners", 40) # ברירת מחדל של 40 איש לסגל, ניתן לשינוי
    
    if name:
        with st.expander(f"📝 פרודוקטים ומחשבון כמויות עבור: {name}"):
            
            # כמות סועדים למנה בסגל
            item_diners = st.number_input(
                f"👥 כמה סועדי סגל יאכלו מנת '{name}'?", 
                min_value=1, 
                value=int(existing_item.get("item_diners", 40)), 
                step=5,
                key=f"{selected_date}_{meal_name}_{category_key}_{item_index}_diners"
            )
            
            st.markdown("---")
            st.markdown("**🍎 רשימת פרודוקטים וצורת הכנה:**")
            
            existing_products = existing_item.get("products", [])
            
            # כותרות הטבלה
            col_p_name, col_p_action, col_p_grams, col_p_total = st.columns([3, 2.5, 2, 2])
            with col_p_name:
                st.caption("שם הפרודוקט")
            with col_p_action:
                st.caption("מה לעשות עם המוצר?")
            with col_p_grams:
                st.caption("גרם לאיש סגל")
            with col_p_total:
                st.caption("סך הכל דרוש")

            action_options = ["➖ ללא פעולה", "🔪 לחתוך", "🥔 לקלף", "🧼 לשטוף בלבד", "🔄 לקלף ולחתוך"]

            # 4 שורות פרודוקטים לכל מנה
            for p_idx in range(4):
                p_data = existing_products[p_idx] if p_idx < len(existing_products) else {"prod_name": "", "action": "➖ ללא פעולה", "grams_per_person": 0.0}
                
                c1, c2, c3, c4 = st.columns([3, 2.5, 2, 2])
                with c1:
                    p_name = st.text_input(f"מוצר {p_idx+1}", value=p_data.get("prod_name", ""), key=f"{selected_date}_{meal_name}_{category_key}_{item_index}_pname_{p_idx}", label_visibility="collapsed", placeholder="למשל: פילה בקר")
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
                        "prod_name": p_name, 
                        "action": p_action,
                        "grams_per_person": p_grams, 
                        "total_kg": total_kg
                    })
            
            st.write("")
            instructions = st.text_area(
                "🥣 הוראות הכנה מיוחדות למנת סגל זו:", 
                value=existing_item.get("instructions", ""), 
                key=f"{selected_date}_{meal_name}_{category_key}_inst_{item_index}",
                placeholder="למשל: להגיש בצלחות אישיות, לקשט בפטרוזיליה..."
            )
            
    return {"name": name, "item_diners": item_diners, "products": updated_products, "instructions": instructions}

# בניית הטאבים של הארוחות
tabs = st.tabs(meals)

for count, meal_name in enumerate(meals):
    with tabs[count]:
        st.subheader(f"🍳 תפריט סגל ל-{meal_name}")
        meal_data = current_menu.get(meal_name, {})
        updated_menu[meal_name] = {}
        
        # 1. סלטים (5 סלטים)
        st.markdown("### 🥗 סלטים (5 סלטים)")
        salads_list = []
        for i in range(5):
            salads_list.append(render_food_item(meal_data, meal_name, "salads", f"סלט {i+1}", i))
        updated_menu[meal_name]["salads"] = salads_list
        
        st.divider()
        
        # 2. עיקריות (3 מנות)
        st.markdown("### 🍗 מנות עיקריות (3 מנות)")
        mains_list = []
        for i in range(3):
            mains_list.append(render_food_item(meal_data, meal_name, "mains", f"מנה עיקרית {i+1}", i))
        updated_menu[meal_name]["mains"] = mains_list

        st.divider()

        # 3. פחמימות (3 פחמימות)
        st.markdown("### 🍚 פחמימות (3 פחמימות)")
        carbs_list = []
        for i in range(3):
            carbs_list.append(render_food_item(meal_data, meal_name, "carb", f"פחמימה {i+1}", i))
        updated_menu[meal_name]["carb"] = carbs_list

        st.divider()

        # 4. קינוח
        st.markdown("### 🍰 קינוח סגל")
        updated_menu[meal_name]["dessert"] = [render_food_item(meal_data, meal_name, "dessert", "שם הקינוח", 0)]

st.divider()

# כפתור שמירה
col_save, col_report = st.columns(2)
with col_save:
    if st.button("💾 שמור תפריט סגל ליום זה", use_container_width=True):
        menus_db[selected_date] = updated_menu
        save_data(menus_db)
        st.success(f"🎉 תפריט הסגל לתאריך {selected_date} נשמר!")

# חלק ב': הפקת דוח עבודה מרוכז ומאוחד לטבחים
with col_report:
    show_report = st.button("📋 הפק תוכנית עבודה יומית למטבח", type="primary", use_container_width=True)

if show_report:
    st.markdown("<div class='report-box'>", unsafe_allow_html=True)
    st.header(f"📋 תוכנית עבודה מרוכזת למטבח הסגל - {selected_date}")
    
    # איסוף ואיחוד כל המוצרים מאותו היום
    aggregated_ingredients = {}
    
    for meal_key, meal_content in updated_menu.items():
        for cat_key, items_list in meal_content.items():
            for item in items_list:
                if item.get("name"): # רק אם המנה הופעלה
                    for prod in item.get("products", []):
                        p_name = prod["prod_name"].strip()
                        p_action = prod["action"]
                        p_weight = prod["total_kg"]
                        
                        # יצירת מפתח משולב של שם המוצר + הפעולה שלו
                        key = (p_name, p_action)
                        if key in aggregated_ingredients:
                            aggregated_ingredients[key] += p_weight
                        else:
                            aggregated_ingredients[key] = p_weight
                            
    if aggregated_ingredients:
        st.markdown("### 🛒 סך הכל פרודוקטים שיש להוציא מהמחסן ולעבד:")
        
        # בניית טבלה יפה להצגה
        report_data = []
        for (p_name, p_action), total_weight in aggregated_ingredients.items():
            report_data.append({
                "פרודוקט": p_name,
                "פעולה נדרשת": p_action,
                "משקל כולל (ק\"ג)": f"{total_weight:,.2f} ק\"ג"
            })
            
        st.table(report_data)
        st.info("💡 הטבלה למעלה מחברת אוטומטית את אותם המוצרים (למשל, אם יש בצל בשני סלטים שונים, היא תציג את סך כל הקילוגרמים של הבצל שצריך לחתוך לאותו היום).")
    else:
        st.warning("לא נמצאו פרודוקטים רשומים ביום זה. ודא שהזנת שמות מנות ופרודוקטים בטאבים למעלה לפני הפקת הדוח.")
    st.markdown("</div>", unsafe_allow_html=True)
