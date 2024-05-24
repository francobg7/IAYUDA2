from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.callbacks.manager import CallbackManager
from langchain_core.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/guia')
def guia():
    return render_template('guia.html')

@app.route('/contactos')
def contactos():
    return render_template('contactos.html')

@app.route('/testimonio')
def testimonio():
    return render_template('testimonio.html')

@app.route('/', methods=['POST'])
def manejar_formulario():
    emit('cargando_respuesta', {'message': 'Generando respuesta, por favor espere...'}, broadcast=True)

    try:
        llm = Ollama(model="gemma", callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]), temperature=0.1)
        nombre = request.form['nombre']
        prompt = PromptTemplate(
            input_variables=["question"],
            template="En cuanto a las preguntas{question}, se un apoyo moral y emocional para las personas. estas para ayudar alas personas en su salud mental y todas las respuestas que das deben ser ordenadas y precisas solo necesitamos respuestas muy cortas y con la eficiencia posible, por que eres AIYUDA un asistente de la salud mental psicologo virtual, solo respondes a lo relacionado a lo psicologico y salud mental"
        )
        sequence = prompt | llm
        response = sequence.invoke({"question": nombre})
        emit('receive_message', {'message': response}, broadcast=True)
    except Exception as e:
        emit('error', {'message': str(e)}, broadcast=True)

@socketio.on('send_message')
def handle_send_message(data):
    message = data['message']
    print(f'Received message: {message}')

    emit('cargando_respuesta', {'message': 'Generando respuesta, por favor espere...'}, broadcast=True)

    try:
        llm = Ollama(model="gemma", callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]), temperature=0.1)
        prompt = PromptTemplate(
            input_variables=["question"],
            template= "En cuanto a las preguntas{question}, se un apoyo moral y emocional para las personas. estas para ayudar alas personas en su salud mental y todas las respuestas que das deben ser ordenadas y precisas solo necesitamos respuestas muy cortas y con la eficiencia posible, por que eres AIYUDA un asistente de la salud mental psicologo virtual, solo respondes a lo relacionado a lo psicologico y salud mental"
        )
        sequence = prompt | llm
        response = sequence.invoke({"question": message})
        emit('receive_message', {'message': response}, broadcast=True)
    except Exception as e:
        emit('error', {'message': str(e)}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)
