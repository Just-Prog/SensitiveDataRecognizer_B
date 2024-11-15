from flask import Blueprint

main = Blueprint('main', __name__)

@main.route('/') 
def home():
    return 'Sensitive Data Recognizer is running.<br/>@Xiamen_Torch_HiTech_IDZ<br/>@SDR_Development_Team, Chengyi University College, Jimei University'