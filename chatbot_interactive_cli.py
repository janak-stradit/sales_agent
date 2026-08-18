"""
Interactive Terminal CLI for Sales AI Chatbot.

Run this script to enter real-time queries in the command line:
    python chatbot_interactive_cli.py
"""

import sys
import requests
import json

sys.stdout.reconfigure(encoding="utf-8")

API_BASE = "http://127.0.0.1:8000/api/v1/chatbot"

def main():
    print("\n" + "=" * 80)
    print(" 🤖 SALES AI INTELLIGENCE CHATBOT — INTERACTIVE TERMINAL")
    print("=" * 80)
    print(" Type your questions in plain English (e.g. 'Who is the CEO of BNY?',")
    print(" 'Find VPs in Asset Servicing', 'Show decision makers with score > 85',")
    print(" or type 'exit' / 'quit' to close).\n")

    while True:
        try:
            query = input("💬 Ask Chatbot > ").strip()
            if not query:
                continue
            if query.lower() in ("exit", "quit", "q"):
                print("\n👋 Goodbye!\n")
                break

            print("   ⏳ Searching warehouse...")
            r = requests.post(
                f"{API_BASE}/message",
                json={"message": query, "include_dossier": True},
                timeout=10
            )

            if r.status_code == 200:
                data = r.json()
                print("\n" + "-" * 75)
                print(f"🤖 [AI ASSISTANT RESPONSE] (Intent: {data.get('intent_detected')})")
                print("-" * 75)
                print(data.get("reply"))
                print("-" * 75)

                # Display top executive cards if available
                people = data.get("people", [])
                if people:
                    print(f"\n📋 [Matched Executive Lead Dossiers: {len(people)}]")
                    for p in people[:3]:
                        print(f"   👤 {p.get('full_name')} | Title: {p.get('title')}")
                        print(f"      ✉️  Email: {p.get('email') or 'N/A'} | 📞 Phone: {p.get('phone') or 'Direct'}")
                        print(f"      🔥 Lead Score: {p.get('lead_score')}/100 | Authority: {p.get('decision_authority') or 'Executive'}")
                        if p.get("communication_style"):
                            print(f"      💡 Comm Style: {p.get('communication_style')}")
                        print()
            else:
                print(f"❌ Error ({r.status_code}): {r.text}\n")

        except KeyboardInterrupt:
            print("\n👋 Exiting...")
            break
        except Exception as e:
            print(f"❌ Connection Error: {e}\n")

if __name__ == "__main__":
    main()
