"""
Aegis Scam Firewall — Machine Learning Training & Benchmarking Pipeline

This script:
1. Curates and loads labeled SMS Scam / Phishing datasets.
2. Performs TF-IDF feature extraction (unigrams + bigrams).
3. Trains and benchmarks 4 Machine Learning models:
   - Multinomial Naive Bayes
   - Logistic Regression
   - Linear Support Vector Classifier (LinearSVC)
   - Random Forest Classifier
4. Compares Precision, Recall, F1-score, and Inference Latency (microseconds).
5. Extracts the most predictive scam tokens & weights.
6. Serializes the best model for deployment.
"""

import os
import sys
import time

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import urllib.request
import zipfile

import io
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

# ---------------------------------------------------------------------------
# 1. Dataset Preparation
# ---------------------------------------------------------------------------

CURATED_DATA = [
    # --- Legitimate / Ham Messages ---
    ("ham", "Hey, are we still meeting for lunch at 12:30 today?"),
    ("ham", "Your doctor appointment with Dr. Smith is confirmed for tomorrow at 3 PM."),
    ("ham", "Mom called, she asked if you can pick up some milk on your way home."),
    ("ham", "The package you ordered was delivered to your front porch."),
    ("ham", "Can you send me the notes from today's lecture when you get a chance?"),
    ("ham", "Thanks for your purchase! Here is your receipt for order #48291."),
    ("ham", "Running about 10 minutes late, see you soon!"),
    ("ham", "Happy birthday! Hope you have a wonderful day celebrating with family."),
    ("ham", "Your ride with Uber has arrived. Driver: Alex in a silver Toyota Camry."),
    ("ham", "Hey man, did you watch the match last night? What an incredible ending!"),
    ("ham", "Your haircut appointment is scheduled for Thursday at 4:30 PM. Reply 1 to confirm."),
    ("ham", "Don't forget to submit the quarterly report before the 5 PM deadline."),
    ("ham", "Your library books are due in 3 days. Renew online or return them to any branch."),
    ("ham", "Dinner was great tonight, thanks for inviting us over!"),
    ("ham", "Good morning! Just checking in to see how you're feeling today."),
    ("ham", "Please find attached the slides from our team meeting earlier."),
    ("ham", "Hey, are you free this weekend to help me move a couple boxes?"),
    ("ham", "Your prescription is ready for pickup at the neighborhood pharmacy."),
    ("ham", "Flight AA1204 is on time. Gate departure B22 at 6:45 PM."),
    ("ham", "Thanks for the heads up, I'll take care of it right away."),
    ("ham", "The gym opens at 6 AM tomorrow if you still want to go."),
    ("ham", "Can I borrow your lawnmower this Saturday for a couple hours?"),
    ("ham", "Great job on the presentation today, everyone was impressed!"),
    ("ham", "I left my sunglasses in your car, can you check if they're there?"),
    ("ham", "Let me know when you land safely so I don't worry."),

    # --- High-Risk Scam & Phishing Messages ---
    ("scam", "URGENT: Your Bank of America account is locked. Verify immediately at http://bit.ly/secure-boa or access will be revoked."),
    ("scam", "IRS Notice: A warrant has been issued for your arrest due to unpaid back taxes. Call 1-800-555-0199 now."),
    ("scam", "USPS: We attempted delivery of your package today. An overdue fee of $2.99 is required at http://track-usps-delivery.xyz"),
    ("scam", "Wells Fargo Alert: A wire transfer of $2,500 was initiated from your account. If this was not you, click http://tinyurl.com/wf-auth"),
    ("scam", "Congratulations! You have been selected as the lucky winner of our $1,000,000 lottery draw. Call now to claim your prize!"),
    ("scam", "Apple Security: Someone signed into your Apple ID from Russia. Confirm your password and OTP here: http://192.168.1.10/apple-login"),
    ("scam", "Geek Squad: Auto-renewal of your tech support plan charged $499.99 to your credit card. Call 888-555-0144 to dispute."),
    ("scam", "Netflix: Your subscription has been suspended due to billing failure. Update payment info at http://netflix-billing-update.top"),
    ("scam", "Social Security Alert: Your SSN has been suspended due to suspected fraudulent activity. Contact an officer immediately."),
    ("scam", "Chase Bank: Unauthorized Zelle transaction of $850 pending. Reply STOP or click http://chase-security-verify.net"),
    ("scam", "DHL Express: Your shipment #849204 has an unpaid customs clearance fee. Pay with prepaid gift cards at http://bit.ly/dhl-pay"),
    ("scam", "Final warning: Legal action will be filed against you in 24 hours unless you settle the outstanding balance of $3,450."),
    ("scam", "Amazon Prime: We detected an unusual order of iPhone 15 for $1,199 on your account. Call support immediately at 800-555-0182"),
    ("scam", "Exclusive offer: Claim your free $500 Target gift card by completing this 1-minute survey: http://cutt.ly/gift-card-win"),
    ("scam", "You have an unclaimed inheritance of $4.5M from a deceased relative. Reply with your full name, bank info, and SSN to begin."),
    ("scam", "PayPal Alert: You sent $750 to Coinbase Inc. If you did not authorize this, call fraud department at 888-555-0177 immediately."),
    ("scam", "Immediate action required: Your account is scheduled for deletion within 12 hours. Unlock now at http://secure-portal-verify.icu"),
    ("scam", "Toll Enforcement: You have an unpaid toll violation of $12.50. Avoid a $50 fine by paying online now: http://toll-ny-pay.work"),
    ("scam", "Federal Court Summons: You have failed to appear for jury duty. A penalty fine of $500 must be paid via Bitcoin wallet to dismiss warrant."),
    ("scam", "FedEx Alert: Delivery failed because address was missing apartment number. Update delivery details here: http://bit.ly/fedex-pack"),
]

def load_or_fetch_dataset():
    """Load the dataset, combining curated fraud patterns with public benchmarks."""
    print("📦 Step 1: Loading Training Dataset...")
    
    # Base dataset from curated examples
    df = pd.DataFrame(CURATED_DATA, columns=["label", "text"])
    
    # Attempt to load UCI SMS Spam dataset if available or download it
    dataset_url = "https://archive.ics.uci.edu/static/public/228/sms+spam+collection.zip"
    cache_path = os.path.join(os.path.dirname(__file__), "sms_spam_collection.csv")
    
    if os.path.exists(cache_path):
        try:
            extra_df = pd.read_csv(cache_path, sep="\t", names=["label", "text"], encoding="utf-8")
            extra_df["label"] = extra_df["label"].map({"ham": "ham", "spam": "scam"})
            df = pd.concat([df, extra_df], ignore_index=True)
            print(f"✅ Loaded cached UCI SMS dataset. Total samples: {len(df)}")
        except Exception as e:
            print(f"⚠️ Could not load cached file: {e}")
    else:
        try:
            print("🌐 Fetching UCI SMS Spam Collection benchmark dataset...")
            req = urllib.request.Request(dataset_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as response:
                zip_data = response.read()
                with zipfile.ZipFile(io.BytesIO(zip_data)) as z:
                    with z.open("SMSSpamCollection") as f:
                        content = f.read().decode("utf-8", errors="ignore")
                        lines = [line.split("\t", 1) for line in content.strip().split("\n") if "\t" in line]
                        extra_df = pd.DataFrame(lines, columns=["label", "text"])
                        extra_df["label"] = extra_df["label"].map({"ham": "ham", "spam": "scam"})
                        extra_df.to_csv(cache_path, sep="\t", index=False)
                        df = pd.concat([df, extra_df], ignore_index=True)
                        print(f"✅ Downloaded & cached UCI dataset. Total samples: {len(df)}")
        except Exception as e:
            print(f"⚠️ Network fetch failed ({e}). Using extended synthetic augmentation.")
            # Augment curated data so we have a strong representative distribution
            augmented = []
            for _ in range(25):
                for label, text in CURATED_DATA:
                    augmented.append((label, text))
            df = pd.DataFrame(augmented, columns=["label", "text"])
            print(f"✅ Augmented dataset ready. Total samples: {len(df)}")

    # Clean text & drop duplicates
    df = df.dropna().drop_duplicates(subset=["text"])
    print(f"📊 Dataset distribution: {dict(df['label'].value_counts())}")
    return df

# ---------------------------------------------------------------------------
# 2. Model Training & Evaluation
# ---------------------------------------------------------------------------

def train_and_benchmark():
    df = load_or_fetch_dataset()

    X = df["text"]
    y = df["label"].map({"ham": 0, "scam": 1})

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    print(f"\n🔢 Split: {len(X_train)} training samples, {len(X_test)} testing samples")

    print("\n⚙️ Step 2: Extracting TF-IDF Features (n-grams 1-2)...")
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=5000,
        sublinear_tf=True,
        stop_words="english"
    )

    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)

    models = {
        "Multinomial Naive Bayes": MultinomialNB(alpha=0.1),
        "Logistic Regression": LogisticRegression(C=5.0, max_iter=500, random_state=42),
        "Linear SVM (LinearSVC)": LinearSVC(C=1.0, random_state=42, dual=False),
        "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42)
    }

    results = []

    print("\n🧠 Step 3: Training & Benchmarking Models...\n")
    print(f"{'Model':<26} | {'Accuracy':<9} | {'Precision':<9} | {'Recall':<9} | {'F1-Score':<9} | {'Latency (µs)':<12}")
    print("-" * 88)

    best_f1 = 0
    best_model_name = ""
    best_pipeline = None

    for name, model in models.items():
        # Train
        model.fit(X_train_tfidf, y_train)

        # Benchmark latency
        t0 = time.perf_counter()
        y_pred = model.predict(X_test_tfidf)
        elapsed_us = ((time.perf_counter() - t0) / len(X_test)) * 1_000_000

        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, zero_division=0)
        rec = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)

        print(f"{name:<26} | {acc * 100:6.2f}%   | {prec * 100:6.2f}%   | {rec * 100:6.2f}%   | {f1 * 100:6.2f}%   | {elapsed_us:7.1f} µs")

        results.append({
            "model": name, "accuracy": acc, "precision": prec, "recall": rec, "f1": f1, "latency_us": elapsed_us
        })

        if f1 > best_f1:
            best_f1 = f1
            best_model_name = name
            best_pipeline = (vectorizer, model)

    print("-" * 88)
    print(f"\n🏆 Best Performing Model: {best_model_name} (F1: {best_f1 * 100:.2f}%)")

    # -----------------------------------------------------------------------
    # 3. Top Scam Predictive Features
    # -----------------------------------------------------------------------
    vec, best_clf = best_pipeline
    if hasattr(best_clf, "coef_"):
        feature_names = np.array(vec.get_feature_names_out())
        coefs = best_clf.coef_[0]
        top_scam_indices = np.argsort(coefs)[-20:][::-1]

        print("\n🔍 Top 20 Most Predictive Scam Features (Learned Weights):")
        for rank, idx in enumerate(top_scam_indices, start=1):
            print(f"  {rank:2d}. {feature_names[idx]:<20} (Weight: +{coefs[idx]:.3f})")

    # -----------------------------------------------------------------------
    # 4. Save Model Artifact
    # -----------------------------------------------------------------------
    save_dir = os.path.join(os.path.dirname(__file__), "models_saved")
    os.makedirs(save_dir, exist_ok=True)
    model_path = os.path.join(save_dir, "scam_classifier_model.joblib")

    joblib.dump({"vectorizer": vec, "model": best_clf, "model_name": best_model_name}, model_path)
    print(f"\n💾 Saved trained model pipeline to: {model_path}")

    # -----------------------------------------------------------------------
    # 5. Live Test on Realistic SMS Edge Cases
    # -----------------------------------------------------------------------
    print("\n🧪 Step 4: Verification Against Realistic Real-World Test Cases:")
    test_cases = [
        "URGENT: Bank of America security alert. Your account has been suspended. Confirm identity at http://bit.ly/secure-auth-update",
        "Hey, don't forget we have soccer practice tomorrow at 5 PM at the community center.",
        "USPS: Package #84920 requires custom fee payment of $3.50. Click http://usps-track-fee.xyz",
        "Can you send me the photos from the family reunion over email?",
        "IRS Notice: You owe $4,500. Pay with Apple gift cards or police will arrest you within 24 hours.",
        "Your verification code for Google is 849201. Do not share this with anyone."
    ]

    for sample in test_cases:
        sample_tfidf = vec.transform([sample])
        pred = best_clf.predict(sample_tfidf)[0]
        if hasattr(best_clf, "predict_proba"):
            prob = best_clf.predict_proba(sample_tfidf)[0][1] * 100
        elif hasattr(best_clf, "decision_function"):
            score = best_clf.decision_function(sample_tfidf)[0]
            prob = (1 / (1 + np.exp(-score))) * 100
        else:
            prob = 100.0 if pred == 1 else 0.0

        label_str = "🚨 SCAM" if pred == 1 else "✅ SAFE"
        print(f"\nMessage: \"{sample}\"")
        print(f"Verdict: {label_str} (Risk Score: {prob:.1f}%)")

if __name__ == "__main__":
    train_and_benchmark()
