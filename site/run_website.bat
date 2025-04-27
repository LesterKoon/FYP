@echo off

REM Navigate to the root of the project
cd site

REM Step 0: Install Python dependencies
REM NOTE: Replace 'D:\Python9\python.exe' with the path to your own Python executable
echo Installing Python dependencies...
echo Installing Python dependencies...
D:\Python9\python.exe -m pip install --upgrade pip
D:\Python9\python.exe -m pip install -r backend\requirements.txt

REM Step 1: Run backend Python scripts in separate windows
REM NOTE: Replace 'D:\Python9\python.exe' with the path to your own Python executable
echo Installing Python dependencies...
echo Starting backend Python files...
start cmd /k "D:\Python9\python.exe backend\add-playlist.py"
start cmd /k "D:\Python9\python.exe backend\get_similar_songs.py"
start cmd /k "D:\Python9\python.exe backend\get_top_songs.py"
start cmd /k "D:\Python9\python.exe backend\save_playlist.py"
start cmd /k "D:\Python9\python.exe backend\chatbot.py"

REM Step 2: Navigate to chatbot and run Rasa commands in separate windows
echo Starting Rasa services...
start cmd /k "cd chatbot && rasa run actions"
start cmd /k "cd chatbot && rasa run --enable-api --cors *"

REM Step 3: Install Node.js dependencies
echo Installing Node.js dependencies...
npm install

REM Step 4: Start the React app
echo Starting React app...
start cmd /k "npm start"

echo All services have been started. Press any key to exit...
pause
