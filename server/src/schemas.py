"""
Marshmallow schemas for request validation.
Each schema matches the features expected by the corresponding ML pipeline.
"""
from marshmallow import Schema, fields, validate, pre_load


class DiabetesPredictionSchema(Schema):
    """BRFSS Diabetes Binary dataset features."""
    HighBP = fields.Float(required=True, validate=validate.OneOf([0, 1]))
    HighChol = fields.Float(required=True, validate=validate.OneOf([0, 1]))
    CholCheck = fields.Float(required=True, validate=validate.OneOf([0, 1]))
    BMI = fields.Float(required=True, validate=validate.Range(min=10, max=100))
    Smoker = fields.Float(required=True, validate=validate.OneOf([0, 1]))
    Stroke = fields.Float(required=True, validate=validate.OneOf([0, 1]))
    HeartDiseaseorAttack = fields.Float(required=True, validate=validate.OneOf([0, 1]))
    PhysActivity = fields.Float(required=True, validate=validate.OneOf([0, 1]))
    Fruits = fields.Float(required=True, validate=validate.OneOf([0, 1]))
    Veggies = fields.Float(required=True, validate=validate.OneOf([0, 1]))
    HvyAlcoholConsump = fields.Float(required=True, validate=validate.OneOf([0, 1]))
    AnyHealthcare = fields.Float(required=True, validate=validate.OneOf([0, 1]))
    NoDocbcCost = fields.Float(required=True, validate=validate.OneOf([0, 1]))
    GenHlth = fields.Float(required=True, validate=validate.Range(min=1, max=5))
    MentHlth = fields.Float(required=True, validate=validate.Range(min=0, max=30))
    PhysHlth = fields.Float(required=True, validate=validate.Range(min=0, max=30))
    DiffWalk = fields.Float(required=True, validate=validate.OneOf([0, 1]))
    Sex = fields.Float(required=True, validate=validate.OneOf([0, 1]))
    Age = fields.Float(required=True, validate=validate.Range(min=1, max=13))
    Education = fields.Float(required=True, validate=validate.Range(min=1, max=6))
    Income = fields.Float(required=True, validate=validate.Range(min=1, max=8))


class HeartPredictionSchema(Schema):
    """UCI Heart Disease dataset features (string categoricals)."""
    age = fields.Float(required=True, validate=validate.Range(min=0, max=120))
    sex = fields.String(required=True, validate=validate.OneOf(['Male', 'Female']))
    cp = fields.String(required=True, validate=validate.OneOf([
        'typical angina', 'atypical angina', 'non-anginal', 'asymptomatic'
    ]))
    trestbps = fields.Float(required=True, validate=validate.Range(min=0, max=300))
    chol = fields.Float(required=True, validate=validate.Range(min=0, max=600))
    fbs = fields.String(required=True, validate=validate.OneOf(['TRUE', 'FALSE']))
    restecg = fields.String(required=True, validate=validate.OneOf([
        'normal', 'st-t abnormality', 'lv hypertrophy'
    ]))
    thalch = fields.Float(required=True, validate=validate.Range(min=0, max=250))
    exang = fields.String(required=True, validate=validate.OneOf(['TRUE', 'FALSE']))
    oldpeak = fields.Float(required=True, validate=validate.Range(min=-5, max=10))
    slope = fields.String(required=True, validate=validate.OneOf([
        'upsloping', 'flat', 'downsloping'
    ]))
    ca = fields.Float(required=True, validate=validate.Range(min=0, max=4))
    thal = fields.String(required=True, validate=validate.OneOf([
        'normal', 'fixed defect', 'reversable defect'
    ]))


class KidneyPredictionSchema(Schema):
    """Chronic Kidney Disease dataset features — all numeric after preprocessing.
    Most fields are optional since the model uses IterativeImputer for missing data.
    """
    age = fields.Float(required=True)
    bp = fields.Float(required=True)
    sg = fields.Float(required=True)
    al = fields.Float(required=True)
    su = fields.Float(required=True)
    rbc = fields.Float(required=True)
    pc = fields.Float(required=True)
    pcc = fields.Float(required=True)
    ba = fields.Float(required=True)
    bgr = fields.Float(required=True)
    bu = fields.Float(required=True)
    sc = fields.Float(required=True)
    sod = fields.Float(required=True)
    pot = fields.Float(required=True)
    hemo = fields.Float(required=True)
    pcv = fields.Float(required=True)
    wc = fields.Float(required=True)
    rc = fields.Float(required=True)
    htn = fields.Float(required=True)
    dm = fields.Float(required=True)
    cad = fields.Float(required=True)
    appet = fields.Float(required=True)
    pe = fields.Float(required=True)
    ane = fields.Float(required=True)




class DepressionPredictionSchema(Schema):
    """Student Depression dataset features."""
    gender = fields.String(required=True, validate=validate.OneOf(['Male', 'Female']))
    age = fields.Float(required=True, validate=validate.Range(min=10, max=80))
    profession = fields.String(required=False, load_default='Student')
    academic_pressure = fields.Float(required=True, validate=validate.Range(min=0, max=5))
    work_pressure = fields.Float(required=True, validate=validate.Range(min=0, max=5))
    cgpa = fields.Float(required=True, validate=validate.Range(min=0, max=10))
    study_satisfaction = fields.Float(required=True, validate=validate.Range(min=0, max=5))
    job_satisfaction = fields.Float(required=True, validate=validate.Range(min=0, max=5))
    sleep_duration = fields.String(required=True, validate=validate.OneOf([
        'Less than 5 hours', '5-6 hours', '7-8 hours', 'More than 8 hours', 'Others'
    ]))
    dietary_habits = fields.String(required=True, validate=validate.OneOf([
        'Unhealthy', 'Moderate', 'Healthy', 'Others'
    ]))
    degree = fields.String(required=False, load_default='BSc')
    suicidal_thoughts = fields.String(required=True, validate=validate.OneOf(['Yes', 'No']))
    work_study_hours = fields.Float(required=True, validate=validate.Range(min=0, max=24))
    financial_stress = fields.Float(required=True, validate=validate.Range(min=0, max=5))
    family_history = fields.String(required=True, validate=validate.OneOf(['Yes', 'No']))
