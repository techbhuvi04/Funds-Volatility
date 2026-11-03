"""
Latest disclosed portfolios (Aug-Oct 2026), equity lines only, % of net assets.
Sources: Groww scheme pages (HDFC, Franklin, UTI, Canara Robeco; pulled 3-4 Nov 2026),
RightAdvise (Kotak Sep-26, quant Aug-26, Motilal Oswal Sep-26), Sharpely (Parag Parikh Sep-26, top 20 only).
Cash, repo, T-bills, G-secs and net payables are excluded. Sector is collapsed to "Fin" (banks, NBFCs,
insurers, AMCs, exchanges, brokers) vs other, because the sources use different taxonomies.
"""
import numpy as np, pandas as pd

F = "Fin"
H = {
"Parag Parikh": dict(n_stocks=None, cash_debt=None, rows=[  # Sep-26, top 20 of portfolio (source shows 20 per page)
 ("HDFC Bank",7.75,F),("Power Grid",5.60,""),("ITC",5.49,""),("Coal India",5.39,""),("ICICI Bank",5.24,F),
 ("Bajaj Holdings",4.96,F),("Kotak Mahindra Bank",4.44,F),("HCL Tech",3.96,""),("M&M",3.89,""),("Infosys",2.93,""),
 ("Bharti Airtel",2.91,""),("Axis Bank",2.85,F),("TCS",2.50,""),("DLF",2.45,""),("Maruti",2.40,""),
 ("Zydus Life",1.54,""),("Cipla",1.33,""),("Dr Reddy's",1.23,""),("IGL",1.22,""),("Zydus Wellness",0.78,"")]),
"HDFC": dict(n_stocks=79, cash_debt=2.74, rows=[
 ("ICICI Bank",8.80,F),("Axis Bank",6.11,F),("HDFC Bank",6.03,F),("SBI",3.94,F),("Eternal",3.46,""),
 ("Kotak Bank",3.40,F),("SBI Life",3.25,F),("L&T",3.08,""),("InterGlobe",2.99,""),("Bharti Airtel",2.62,""),
 ("Maruti",2.57,""),("Cipla",2.47,""),("HCL Tech",2.44,""),("Eicher",2.30,""),("Power Grid",2.11,""),
 ("Hyundai India",1.68,""),("Divi's",1.62,""),("Max Healthcare",1.46,""),("JSW Steel",1.45,""),("Reliance",1.40,""),
 ("Piramal Pharma",1.37,""),("Persistent",1.32,""),("Bosch",1.30,""),("PB Fintech",1.12,F),("TVS Motor",0.96,"")]),
"Kotak": dict(n_stocks=55, cash_debt=None, rows=[
 ("ICICI Bank",5.48,F),("BEL",5.34,""),("HDFC Bank",5.27,F),("SBI",4.30,F),("Eternal",4.22,""),
 ("Jindal Steel",4.06,""),("Solar Inds",3.71,""),("L&T",3.54,""),("Axis Bank",3.35,F),("SRF",2.89,""),
 ("Bharti Airtel",2.88,""),("UltraTech",2.84,""),("InterGlobe",2.53,""),("Bharat Forge",2.39,""),("Zydus Life",2.28,""),
 ("Reliance",2.24,""),("Sun Pharma",2.14,""),("Lenskart",2.08,""),("Bajaj Finance",1.99,F),("Hero Moto",1.97,""),
 ("BSE",1.81,F),("Maruti",1.80,""),("AU SFB",1.69,F),("Infosys",1.60,""),("Kotak Bank",1.45,F),
 ("IndusInd",1.27,F),("Billionbrains",1.14,F),("Shriram Fin",1.11,F),("Max Fin",0.70,F),("Piramal Fin",0.69,F),("360 One",0.60,F)]),
"quant": dict(n_stocks=27, cash_debt=None, rows=[  # Aug-26
 ("Samvardhana Motherson",9.63,""),("Adani Enterprises",7.87,""),("Adani Power",7.72,""),("Aurobindo",7.01,""),
 ("ICICI Pru AMC",5.61,F),("Adani Green",3.46,""),("Adani Energy Sol",3.40,""),("Bharti Airtel",2.83,""),
 ("Tata Power",2.77,""),("KPR Mill",2.11,""),("Alivus",2.08,""),("JSW Infra",1.84,""),("ICICI Bank",1.82,F),
 ("DLF",1.75,""),("Swan Corp",1.68,""),("LG Elec India",1.36,""),("Zydus Life",1.34,""),("Indus Towers",1.22,""),
 ("Piramal Fin",1.16,F),("BHEL",1.13,""),("Sona BLW",0.89,""),("Lloyds Metals",0.62,""),("ABLBL",0.47,""),
 ("Tata Comm",0.31,""),("IRB Infra",0.30,""),("Tata Chem",0.28,""),("Nippon AMC",0.18,F)]),
"Franklin India": dict(n_stocks=57, cash_debt=5.28, rows=[
 ("ICICI Bank",6.46,F),("Axis Bank",5.27,F),("HDFC Bank",5.24,F),("L&T",3.82,""),("SBI",3.43,F),
 ("Bharti Airtel",3.32,""),("Eternal",3.20,""),("Kotak Bank",3.12,F),("M&M",3.09,""),("Reliance",2.93,""),
 ("Infosys",2.54,""),("Apollo Hosp",2.52,""),("Kirloskar Oil",2.34,""),("Marico",2.07,""),("BEL",2.02,""),
 ("HCL Tech",2.00,""),("Tata Steel",1.99,""),("Cipla",1.92,""),("Tata Power",1.90,""),("HAL",1.83,""),
 ("IIFL Wealth",1.22,F),("Tata Capital",1.22,F),("SBFC",0.61,F),("PB Fintech",0.51,F)]),
"Canara Robeco": dict(n_stocks=83, cash_debt=3.73, rows=[
 ("ICICI Bank",6.62,F),("HDFC Bank",6.48,F),("Bharti Airtel",3.78,""),("Reliance",3.43,""),("L&T",3.11,""),
 ("Eternal",2.99,""),("Bajaj Finance",2.97,F),("Axis Bank",2.51,F),("Infosys",2.50,""),("SBI",2.42,F),
 ("M&M",2.37,""),("Divi's",1.90,""),("Kotak Bank",1.68,F),("TVS Motor",1.67,""),("Indian Hotels",1.61,""),
 ("Torrent Pharma",1.51,""),("Chola Inv",1.47,F),("Max Healthcare",1.44,""),("Sun Pharma",1.41,""),("Lenskart",1.40,""),
 ("MCX",1.18,F),("Max Fin",0.99,F),("Shriram Fin",0.92,F),("HDFC AMC",0.89,F),("Billionbrains",0.68,F),
 ("CAMS",0.55,F),("PB Fintech",0.42,F),("SBI Life",0.32,F),("AU SFB",0.22,F),("Vysya Housing",0.17,F)]),
"UTI": dict(n_stocks=53, cash_debt=2.98, rows=[
 ("Eternal",6.56,""),("ICICI Bank",5.81,F),("Bajaj Finance",5.53,F),("HDFC Bank",4.61,F),("Titan",3.94,""),
 ("Coforge",3.77,""),("Dixon",3.61,""),("Info Edge",3.59,""),("Persistent",3.44,""),("Kotak Bank",3.41,F),
 ("Bharti Airtel",3.37,""),("DMart",2.84,""),("M&M",2.44,""),("Dr Lal Path",2.22,""),("Eicher",2.19,""),
 ("Ajanta",2.12,""),("Trent",2.10,""),("Maruti",2.06,""),("LTIMindtree",2.05,""),("Global Health",2.00,""),
 ("Chola Inv",1.45,F),("AU SFB",1.03,F),("Aavas",0.69,F)]),
"Motilal Oswal": dict(n_stocks=31, cash_debt=3.26, rows=[
 ("Kalyan Jewellers",8.23,""),("Eternal",6.54,""),("CG Power",5.65,""),("Sterlite Tech",4.43,""),("Coforge",4.36,""),
 ("Diamond Power",3.97,""),("Aditya Infotech",3.86,""),("Shriram Fin",3.82,F),("MCX",3.77,F),("Ather",3.20,""),
 ("RBL Bank",3.16,F),("Persistent",3.09,""),("IndusInd",3.05,F),("Waaree",3.00,""),("Siemens",2.77,""),
 ("Onesource",2.71,""),("Acutaas",2.65,""),("Lalithaa",2.50,""),("Ola Electric",2.50,""),("HDFC AMC",2.45,F),
 ("Muthoot",2.12,F),("Piramal Fin",1.82,F),("ICICI Pru AMC",1.45,F)]),
}

def conc_table():
    out = {}
    for f, d in H.items():
        rows = sorted(d["rows"], key=lambda r: -r[1])
        w = pd.Series({n: x for n, x, _ in rows}) / 100
        top20 = w.iloc[:20]
        fin = sum(x for _, x, s in rows[:20] if s == F) / 100   # financials within top 20
        out[f] = dict(
            n_stocks=d["n_stocks"], top1=w.iloc[0], top5=w.iloc[:5].sum(), top10=w.iloc[:10].sum(),
            top20=top20.sum(), hhi_top20=(top20 ** 2).sum() * 1e4,  # in bps^2-style points (sum of %^2)
            eff_n_top20=top20.sum() ** 2 / (top20 ** 2).sum(),   # effective names within top 20
            fin_in_top20=fin,
        )
    t = pd.DataFrame(out).T
    t.loc["quant", "group_note"] = "Adani group 22.4%"
    return t

if __name__ == "__main__":
    t = conc_table(); t.to_csv("concentration.csv")
    print(t.to_string(float_format=lambda x: f"{x:.3f}"))
    print("Adani group in quant:", 7.87 + 7.72 + 3.46 + 3.40)
