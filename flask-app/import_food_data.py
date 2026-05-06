import pandas as pd
from flaskr import create_app, db
from flaskr.models import Food


def import_cofid():
    app = create_app()

    with app.app_context():
        file_path = 'food_data.xlsx'
        sheet_name = '1.3 Proximates'
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        df = df.drop([0, 1]).reset_index(drop=True)

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

        print("Clearing existing food records...")
        Food.query.delete()
        db.session.commit()

        for index, row in df.iterrows():
            exists = Food.query.filter_by(food_id=row['Food Code']).first()
            if exists:
                continue
            food = Food(
                food_id=row['Food Code'],
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
