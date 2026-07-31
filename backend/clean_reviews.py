import pandas as pd

# Apni asal CSV file ka path
input_file = r"C:\Users\adnan\Downloads\archive\olist_order_reviews_dataset.csv"

# Output cleaned file Uploads folder mein seedha save hogi
output_file = r"C:\ProgramData\MySQL\MySQL Server 8.0\Uploads\olist_order_reviews_cleaned.csv"

df = pd.read_csv(input_file)

df['review_comment_title'] = df['review_comment_title'].astype(str).str.replace('\n', ' ', regex=False).str.replace('\r', ' ', regex=False)
df['review_comment_message'] = df['review_comment_message'].astype(str).str.replace('\n', ' ', regex=False).str.replace('\r', ' ', regex=False)

df.to_csv(output_file, index=False)
print("Done! Cleaned file saved at:", output_file)