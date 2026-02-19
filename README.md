"""Para actualizar los cambios que se van haciendo.
    git status
    git add .
    git commit -m "Descripción de cambios
    git push origin main"""

#primero instalar python version 3.12
#luego crear un entorno virtual
py -3.12 -m venv venv
# luego activar el entorno virtual
.\venv\Scripts\Activate
# luego intalar django dentro del venv
pip install django
# luego hacer migracion y iniciar
python manage.py migrate
python manage.py runserver

#para la api primero instalamos
pip install djangorestframework

#instalamos JWT
pip install djangorestframework-simplejwt

#ahora instalamos customTkinter que es la app de escritorio
pip install customtkinter requests
# despues instalamos este
pip install PySide6 requests
# ingresar al entorno virtual de la pagina de escritorio
.\venv\Scripts\Activate
cd bienestar_desktop
# al estar en el entorno virtual de la app de escritorio
python main.py
# nos pedira un gmail y contraseña y debemos ingresar cualquiera que ya este registrada en la app web de django
#para volver a la maquina virtual de la aplicacion web de django ingresamos
deactivate
cd ..
python manage.py runserver 0.0.0.0:8000
# luego debes ingresar a la normal que es esta 
http://127.0.0.1:8000/
