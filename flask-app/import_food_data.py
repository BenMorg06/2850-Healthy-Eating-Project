import pandas as pd
import time
from flaskr import create_app, db
from flaskr.models import Food

def import_cofid():
    app = create_app()

    with app.app_context():
        file_path = 'food_data.xlsx'
        sheet_name = '1.3 Proximates'
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        #print(df.head())
        '''
        new_cols = [str(code) if pd.notna(code) else col for col,code in zip(df.columns, df.iloc[0])]
        df.columns = new_cols
        '''
        #print(df.head())
        #print(df['Protein (g)'])
        df = df.drop([0,1]).reset_index(drop=True)

        numeric_cols = [
            'Protein (g)',
            'Carbohydrate (g)',
            'Total sugars (g)',
            'Fat (g)',
            'Energy (kcal) (kcal)',
            'Energy (kJ) (kJ)',
            'AOAC fibre (g)'
        ]

        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)

        #print(df.head())

        print("Clearing existing food records...")
        Food.query.delete() # This removes all old rows from the food table
        db.session.commit()

        for index, row in df.iterrows():
            exists = Food.query.filter_by(food_id=row['Food Code']).first()
            if exists:
                continue
            food = Food(
                food_id = row['Food Code'],
                food_name=row['Food Name'],
                kcal=row['Energy (kcal) (kcal)'],
                kj=row['Energy (kJ) (kJ)'],
                carbs=row['Carbohydrate (g)'],
                protein=row['Protein (g)'],
                fats=row['Fat (g)'],
                sugar=row['Total sugars (g)'],
                fibre=row['AOAC fibre (g)']
            )
            db.session.add(food)
        db.session.commit()

if __name__ == '__main__':
    import_cofid()