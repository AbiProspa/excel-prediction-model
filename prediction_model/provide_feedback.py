import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from feedback_loop import update_weights, load_weights

def main():
    print("="*50)
    print("HYBRID AI FEEDBACK LOOP")
    print("="*50)
    
    current_weights = load_weights()
    print(f"Current Weights: {current_weights}")
    print("-" * 50)
    print("Did the model make a CORRECT prediction regarding High Risk?")
    print("Press 'y' for YES (Model was right, trust Sentiment more)")
    print("Press 'n' for NO  (Model was wrong, trust Rating/Rules more)")
    
    choice = input("\nEnter choice (y/n): ").strip().lower()
    
    if choice == 'y':
        print("\nUpdating weights: REINFORCING Sentiment Analysis...")
        update_weights(prediction_correct=True)
    elif choice == 'n':
        print("\nUpdating weights: CORRECTING with Standard Ratings...")
        update_weights(prediction_correct=False)
    else:
        print("Invalid choice. Exiting.")
        return

    new_weights = load_weights()
    print("-" * 50)
    print(f"New Weights:     {new_weights}")
    print("="*50)
    print("✅ Learning updated.")

if __name__ == "__main__":
    main()
