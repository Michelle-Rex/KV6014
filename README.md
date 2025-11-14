In order to run this project for dev or test pursposes I would suggest the following method but first please make sure you have installed "Docker" or "Docker Desktop":



1. Open powershell and navigate to the work folder using "cd C://folder/to/project"
2. You will first need to build the docker container from the 'dockerfile' so run "docker build -t ANY-NAME-YOU-WANT ."
3. Then to run it you should use "docker run -it -v "${PWD}:/workspace" -p 8501:8501 ANY-NAME-YOU-WANT" that way it updates the actual files rather than being isolated, it should also open the port 8501.
4. Once insisde you will need to run "python3 -m pip install pandas streamlit" to install the required python modules
5. After that you are free to modify the files however you want! to run it though you should do: "streamlit run app.py"





Todo: make a better readme

