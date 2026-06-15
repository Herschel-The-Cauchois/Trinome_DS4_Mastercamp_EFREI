import pandas as pd
import smtplib
from email.mime.text import MIMEText

df = pd.read_csv("/mnt/data/ANSSI_cleaned.csv", sep=";", engine="python", on_bad_lines="skip")

df["CVSS"] = pd.to_numeric(df["CVSS"], errors="coerce")
df["EPSS"] = pd.to_numeric(df["EPSS"], errors="coerce")

critical = df[
    (df["CVSS"] >= 8) | (df["EPSS"] >= 0.6)
].copy()


subscribers = {
    "apache": ["apache_team@company.com"],
    "openssl": ["crypto_team@company.com"],
    "windows": ["windows_team@company.com"]
}

def match_software(text):
    text = str(text).lower()
    for software in subscribers.keys():
        if software in text:
            return software
    return None

critical["software"] = critical["Title"].fillna("") + " " + critical["CVE Description"].fillna("")
critical["software"] = critical["software"].apply(match_software)

critical = critical.dropna(subset=["software"])
critical["score"] = 0.6 * critical["EPSS"].fillna(0) + 0.4 * (critical["CVSS"].fillna(0) / 10)

# from_email = "votre_email@gmail.com"
# password = "mot_de_passe_application"

# server = smtplib.SMTP("smtp.gmail.com", 587)
# server.starttls()
# server.login(from_email, password)

for software, emails in subscribers.items():

    alerts = critical[critical["software"] == software]

    if alerts.empty:
        continue

    body = f"""
ALERTE SÉCURITÉ - {software.upper()}

Des vulnérabilités critiques ont été détectées sur {software}.

Détails :
"""

    for _, row in alerts.iterrows():
        body += f"""
- {row['CVE']}
  Score: {row['score']:.3f}
  CVSS: {row['CVSS']}
  EPSS: {row['EPSS']}
  Description: {str(row['CVE Description'])[:200]}...
"""

    body += "\nAction recommandée : patch immédiat ou mitigation.\n"

    for email in emails:
        msg = MIMEText(body)
        msg["From"] = from_email
        msg["To"] = email
        msg["Subject"] = f"🚨 ALERTE CRITIQUE - {software}"

        # server.sendmail(from_email, email, msg.as_string())
        print(msg.as_string())

# server.quit()