import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import json
import os
from enum import Enum
from typing import Optional
from dataclasses import dataclass

class DanceStyle(Enum):
    BALLET = "Ballet"
    JAZZ = "Jazz"
    TAP = "Tap"
    HIPHOP = "HipHop"
    CONTEMPORARY = "Contemporary"

class AgeGroup(Enum):
    AGE_3_4 = "3 - 4"
    AGE_5_7 = "5 - 7"
    AGE_8_11 = "8 - 11"
    AGE_12_18 = "12 - 18"
    AGE_18_PLUS = "18+"

class CompanyDance(Enum):
    MOTION_MANIA = "Motion Mania"
    DIAMOND_COMPANY = "Diamonds"
    SAPPHIRE_COMPANY = "Sapphires"
    OPAL_COMPANY = "Opals"
    CRYSTAL_COMPANY = "Crystals"
    RUBY_COMPANY = "Rubies"
    EMERALD_COMPANY = "Emeralds"
    DAD_DANCE = "Dad Dance"
    NEITHER = "Neither"

@dataclass
class DanceNumber:
    name: str
    style: DanceStyle
    age_group: AgeGroup
    dancers: list[str]
    is_difficult: bool
    is_company_jazz: bool
    company_dance: CompanyDance
    duration: Optional[str] = None
    teacher: Optional[str] = None
    class_time: Optional[str] = None

    def display(self):
        print("\n--- Dance Number ---")
        print(f"  Name:          {self.name}")
        print(f"  Style:         {self.style.value}")
        print(f"  Age Group:     {self.age_group.value}")
        print(f"  Dancers:       {', '.join(self.dancers)}")
        print(f"  Difficulty:    {'Yes' if self.is_difficult else 'No'}")
        print(f"  Company Jazz:  {'Yes' if self.is_company_jazz else 'No'}")
        print(f"  Company Dance:  {self.company_dance.value}")
        if self.duration:
            print(f"  Duration:      {self.duration}")
        if self.teacher:
            print(f"  Teacher:       {self.teacher}")
        if self.class_time:
            print(f"  Class Time:       {self.class_time}")


st.title("Dance Data Uploader")

uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx"])

if uploaded_file is not None:
    sheet_names = pd.ExcelFile(uploaded_file).sheet_names

    if len(sheet_names) > 1:
        sheet = st.selectbox("Select a sheet", sheet_names)
    else:
        sheet = sheet_names[0]

    df = pd.read_excel(uploaded_file, sheet_name=sheet)

    st.success(f"Loaded **{len(df)} rows** and **{len(df.columns)} columns** from sheet *{sheet}*")
    st.dataframe(df, use_container_width=True)

    save_file_json = "dances_output.json"
    base = os.path.dirname(os.path.abspath(__file__))
    save_path = os.path.join(base, save_file_json)

    records = df.copy()
    if "dancers" in records.columns:
        records["dancers"] = records["dancers"].apply(
            lambda x: [name.strip() for name in str(x).split(",")] if pd.notna(x) else []
        )

    def replace_nan(obj):
        if isinstance(obj, float) and np.isnan(obj):
            return None
        if isinstance(obj, dict):
            return {k: replace_nan(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [replace_nan(i) for i in obj]
        return obj

    with open(save_path, "w") as f:
        json.dump(replace_nan(records.to_dict(orient="records")), f, indent=2)

    st.info(f"Data saved to `{save_path}`")

def organize_dances(dance_numbers: list[DanceNumber], gap: int = 2) -> list[DanceNumber] | None:
     
    if len(dance_numbers) <= 1:
        return dance_numbers[:]

    remaining = list(range(len(dance_numbers)))

    diamond = [i for i in remaining if dance_numbers[i].company_dance == CompanyDance.DIAMOND_COMPANY]

    for i in diamond:
        remaining.remove(i)
        remaining.append(i)

    result_indices = []
    last_dad_dance = -1

    def is_valid_candidate(i: int) -> bool:
        """Return True if dance i doesn't reuse any dancer from the last `gap` placed dances."""
        if dance_numbers[i].is_difficult == True:
            gap_current = 3
        else:
            gap_current = gap
        dancers_i = set(dance_numbers[i].dancers)
        for placed in result_indices[-gap_current:]:
            if set(dance_numbers[placed].dancers) & dancers_i:
                return False
        for place in result_indices[-1:]:
            if dance_numbers[place].style != dance_numbers[i].style:
                return True
            else:
                return False
            
    def is_valid_candidate_wo_style(i: int) -> bool:
        """Return True if dance i doesn't reuse any dancer from the last `gap` placed dances."""
        if dance_numbers[i].is_difficult == True:
            gap_current = 3
        else:
            gap_current = gap
        dancers_i = set(dance_numbers[i].dancers)
        for placed in result_indices[-gap_current:]:
            if set(dance_numbers[placed].dancers) & dancers_i:
                return False
        return True

    for k in remaining:
        if dance_numbers[k].company_dance == CompanyDance.MOTION_MANIA:
            motion_mania = k
            #result_indices.append(k)
            #remaining.remove(k)
        if dance_numbers[k].company_dance == CompanyDance.DAD_DANCE:
            last_dad_dance = k
            #remaining.remove(k)
    
    result_indices.append(motion_mania)
    remaining.remove(motion_mania)
    remaining.remove(last_dad_dance)

    while remaining:
        if result_indices:
            
            candidates = [i for i in remaining if is_valid_candidate(i)]
            
        else:
            candidates = list(remaining)

        if not candidates:
            
            candidates2 = [i for i in remaining if is_valid_candidate_wo_style(i)]
            if not candidates2:
                return None
            else:
                candidates = candidates2

        # Prefer the candidate that conflicts with the most remaining dances to avoid dead ends
        def conflict_count(i):
            dancers_i = set(dance_numbers[i].dancers)
            #return sum(1 for j in remaining if j != i and set(dance_numbers[j].dancers) & dancers_i)
            count = 0
            for j in remaining:
                if j != i:
                    shared_dancers = set(dance_numbers[j].dancers) & dancers_i
                    if shared_dancers and dance_numbers[i].company_dance != CompanyDance.DIAMOND_COMPANY:
                        count += 1
            return count
            
                
        best = max(candidates, key=conflict_count)
        result_indices.append(best)
        remaining.remove(best)



    if  last_dad_dance != -1 :  
      result_indices.append(last_dad_dance)
    return [dance_numbers[i] for i in result_indices]

def load_dances(path: str) -> list[DanceNumber]:
    with open(path) as f:
        data = json.load(f)
    dances = []
    for r in data:
        dances.append(DanceNumber(
            name=r["name"],
            style=DanceStyle(r["style"]),
            age_group=AgeGroup(r["age_group"]),
            dancers=r["dancers"] or [],
            is_difficult=bool(r["is_difficult"]),
            is_company_jazz=bool(r["is_company_jazz"]),
            company_dance=CompanyDance(r["company_dance"]),
            duration=r.get("duration"),
            teacher=r.get("teacher"),
            class_time=r.get("class_time"),
        ))
    return dances

def save_dances_xlsx(dances: list[DanceNumber], path: str):
    rows = [{
        "name": d.name,
        "style": d.style.value,
        "age_group": d.age_group.value,
        "dancers": ", ".join(d.dancers),
        "is_difficult": d.is_difficult,
        "is_company_jazz": d.is_company_jazz,
        "company_dance": d.company_dance.value,
        "duration": d.duration,
        "teacher": d.teacher,
        "class_time": d.class_time,
    } for d in dances]
    pd.DataFrame(rows).to_excel(path, index=False)

if st.button("Order the Dances"):
    base = os.path.dirname(os.path.abspath(__file__))
    save_path = os.path.join(base, "dances_output.json")
    dance_numbers = load_dances(save_path)
    if len(dance_numbers) < 2:
        st.error("Need at least 2 dance numbers to organize.")
    else:
        organized = organize_dances(dance_numbers)
        if organized is None:
            st.error("Cannot arrange dances to satisfy the constraint — a dancer appears in too many consecutive numbers.")
        else:
            st.session_state["organized"] = organized

if "organized" in st.session_state:
    organized = st.session_state["organized"]
    st.subheader("Suggested Order")
    for i, dance in enumerate(organized, 1):
        st.write(f"{i}. **{dance.name}** — {', '.join(dance.dancers)} — {'Difficult' if dance.is_difficult else 'Standard'}")

    if st.button("Save this order"):
        st.session_state["saving"] = True

    if st.session_state.get("saving"):
        file_name = st.text_input("Enter a file name (without extension):", key="save_file_name")
        if st.button("Confirm Save") and file_name:
            base = os.path.dirname(os.path.abspath(__file__))
            xlsx_out = os.path.join(base, f"{file_name}.xlsx")
            save_dances_xlsx(organized, xlsx_out)
            st.success(f"Order saved to `{xlsx_out}`.")
            st.session_state["saving"] = False
