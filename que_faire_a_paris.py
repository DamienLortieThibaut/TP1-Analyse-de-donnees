import pandas as pd
import matplotlib.pyplot as plt
from sklearn import tree
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import plot_tree
from collections import Counter
import re

# Charger le fichier CSV
df = pd.read_csv('que-faire-a-paris-.csv', sep=';')

# Gardons uniquement les colonnes principales pour l'analyse demandée
essential_columns = [
    'ID', 'Titre', 'Chapeau', 'Description', 'Date de début', 'Date de fin', 'Mots clés',
    'audience', 'Type de prix'
]

# Filtrage des colonnes et suppression des lignes avec des valeurs nulles dans ces colonnes
df_cleaned = df[essential_columns].dropna()

print("Voici les 5 premières lignes du dataset")
print(df_cleaned.head())

print("Nombre d'évenements à Paris: ", df_cleaned["ID"].count())

# Extraction des mots-clés de la colonne "Mots clés"
keywords = df_cleaned['Mots clés'].dropna().str.lower()
keywords = keywords.apply(lambda x: re.split(r'[,;| ]+', x))  # Séparer par virgule, point-virgule ou espace

# Aplatir la liste de listes pour obtenir une liste simple de mots-clés
all_keywords = [keyword for sublist in keywords for keyword in sublist]

# Compter la fréquence de chaque mot-clé
keyword_counts = Counter(all_keywords)

# Convertir en DataFrame pour une visualisation facile
keyword_df = pd.DataFrame(keyword_counts.items(), columns=['Keyword', 'Count'])
keyword_df = keyword_df.sort_values(by='Count', ascending=False).head(20)  # Les 20 mots-clés les plus fréquents

# Création d'une palette de couleurs dégradées pour le graphique
colors = plt.cm.Blues([0.1 + 0.9 * (i / len(keyword_df)) for i in range(len(keyword_df))])

# Afficher les mots-clés les plus fréquents sous forme de graphique avec un dégradé de couleur
plt.figure(figsize=(12, 8))
plt.barh(keyword_df['Keyword'], keyword_df['Count'], color=colors)
plt.xlabel('Fréquence')
plt.ylabel('Mot-clé')
plt.title('Top 20 des mots-clés les plus fréquents')
plt.gca().invert_yaxis()
plt.show()

# Comptage des événements par type de prix
price_type_counts = df_cleaned['Type de prix'].value_counts()

# Création du pie chart
plt.figure(figsize=(8, 8))
plt.pie(
    price_type_counts,
    labels=price_type_counts.index,
    autopct='%1.1f%%',
    startangle=140,
    colors=plt.cm.Pastel1.colors
)
plt.title('Répartition des types de prix des événements')
plt.show()

# Sélectionner les 5 mots-clés les plus fréquents
top_keywords = [keyword for keyword, _ in keyword_counts.most_common(5)]

# Créer des colonnes binaires pour ces mots-clés
for keyword in top_keywords:
    df_cleaned[keyword] = df_cleaned['Mots clés'].apply(lambda x: 1 if keyword in x else 0)

# Encoder la colonne 'audience'
audience_encoder = LabelEncoder()
df_cleaned['audience'] = audience_encoder.fit_transform(df_cleaned['audience'])

# Encoder la colonne 'Type de prix'
price_type_encoder = LabelEncoder()
df_cleaned['Type de prix'] = price_type_encoder.fit_transform(df_cleaned['Type de prix'])

# Préparer les données pour l'arbre de décision
X_reduced = df_cleaned[top_keywords + ['audience']]  # Caractéristiques réduites
y = df_cleaned['Type de prix']  # Label

# Création et entraînement de l'arbre de décision avec une profondeur limitée
clf = tree.DecisionTreeClassifier(max_depth=2)  # Limite la profondeur à 3 pour simplifier l'affichage
clf = clf.fit(X_reduced, y)

# Visualisation de l'arbre
plt.figure(figsize=(20, 10))
plot_tree(clf, feature_names=X_reduced.columns, class_names=price_type_encoder.classes_, filled=True, fontsize=10)
plt.title("Arbre de décision pour prédire le type de prix basé sur les mots-clés et l'audience (profondeur limitée)")
plt.show()

# Exemple de prédiction (à ajuster selon les mots-clés présents et l'audience encodée)
new_event = [[1, 0, 1, 0, 1, 2]]  # Exemple : valeurs binaires pour les mots-clés et l'audience encodée
predicted_price_type = clf.predict(new_event)
predicted_price_type_decoded = price_type_encoder.inverse_transform(predicted_price_type)
print("Le type de prix prédit pour le nouvel événement est :", predicted_price_type_decoded)