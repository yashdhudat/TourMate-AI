import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer # type: ignore

# Load your cleaned file (like from 'Expanded_Destinations.csv')
df = pd.read_csv(r'C:\Users\Death Note\Downloads\archive (1)\Expanded_Destinations.csv')

# Manual mappings
df['Climate'] = df['State'].map({
    'Goa': 'Warm', 'Kerala': 'Warm', 'Uttar Pradesh': 'Moderate',
    'Rajasthan': 'Warm', 'Jammu and Kashmir': 'Cold'
}).fillna('Moderate')

df['Budget'] = df['Type'].map({
    'Historical': 'Medium', 'Beach': 'Medium', 'City': 'High',
    'Nature': 'Low', 'Adventure': 'Medium'
}).fillna('Medium')

df['Suitable_For'] = df['Type'].map({
    'Historical': 'Solo;Couple;Family', 'Beach': 'Couple;Group;Family',
    'City': 'Solo;Couple;Group', 'Nature': 'Family;Group',
    'Adventure': 'Solo;Group'
}).fillna('Solo;Couple')

df['Activities'] = df['Type'].map({
    'Historical': 'History;Culture;Sightseeing',
    'Beach': 'Beaches;Relaxation;Nightlife',
    'City': 'Shopping;Culture;Food',
    'Nature': 'Nature;Relaxation',
    'Adventure': 'Trekking;Adventure;Nature'
}).fillna('Sightseeing;Culture')

# Reduce and rename
df = df[['Name', 'State', 'Climate', 'Budget', 'Activities', 'Suitable_For']]
df.rename(columns={'Name': 'Destination', 'State': 'Country'}, inplace=True)

# Split and encode
df['Activities'] = df['Activities'].apply(lambda x: [i.strip() for i in x.split(';')])
df['Suitable_For'] = df['Suitable_For'].apply(lambda x: [i.strip() for i in x.split(';')])
df = pd.get_dummies(df, columns=['Climate', 'Budget'])

mlb_a = MultiLabelBinarizer()
mlb_s = MultiLabelBinarizer()

a_encoded = pd.DataFrame(mlb_a.fit_transform(df['Activities']), columns=mlb_a.classes_)
s_encoded = pd.DataFrame(mlb_s.fit_transform(df['Suitable_For']), columns=mlb_s.classes_)

df_final = pd.concat([
    df[['Destination', 'Country']],
    df.drop(['Destination', 'Country', 'Activities', 'Suitable_For'], axis=1),
    a_encoded, s_encoded
], axis=1)

# Save final vector
df_final.to_csv('destination_vectors.csv', index=False)
print("✅ Saved as destination_vectors.csv")
