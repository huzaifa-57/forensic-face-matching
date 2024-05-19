# Forensic Face Matching at Airports during Passport Control
Checking the originality of the passport by taking a scanned image of the passport data page as input. Then extract the passport number from it and search for the number in the database. If the passport number matches the system gets the image associated with it. After the database image is found, detect the face from the scanned passport, and compare both images, if both mages are matched, then the passport is considered valid. After this verification takes a live photo of the passenger, does necessary pre-processing, and again compare with the database image for Person verification (Age-invariant Face Recognition).

### Requirments
* Python 3.7+
* PyTorch
* TorchVision
* Numpy
* Pandas
* FPDF
* Passport Eye
* PyTesseract
* Webbrowser
* Filetype
* Dlib
* OpenCV
* PyQt6
* Pillow
* SQLite3

### Installing
To install required libraries, run the followinf command in command line:
```sh
pip install -r requirements.txt
```
You may face some errors while installing Tesseract-OCR. Manually download the Tesseract-OCR and then enter the installation path in environmental variables (e.g. The default address is `C:\Program Files\Tessetact-OCR)`

### Getting Started
The model is not available in with the following sorce code. You have yo manually dowload the pre-trained models. Below is the link to download the model:
- model - [Google Drive](https://drive.google.com/drive/folders/18PG9vUkIrZ-m_kwWJKvv6pmIVicRSN9O?usp=sharing)

_(Note: Download and save the files in the folder `model`)_

The Intelligent Face capturing requires face detectors to process. The detectors also needed to be download. Download detectors from the given link below
- detectors - [Google Drive](https://drive.google.com/drive/folders/1kbCLelfO6mHTHkhp4AQ-TR4Y-wzu5QGO?usp=sharing)

_(Note: Download and save the files in the folder `detectors`)_

The work is not over yet. Copy the downloaded file and move them to their respective folders. Place both `model` and `detectors` folders in the `\Resources` folder)

In the last project needs another folder that must and should be available. Without that folder and files project is not able to run. Download that folder from the below link
- mtlface - [Google Drive](https://drive.google.com/drive/folders/1hZIsy-6NkqF2zwDUWoo6vi6VPjm8lnwF?usp=sharing)

_(Note: Place `mtlface` folder in the root directory)_

If you have any queries regarding that feel free to contact us. We will help you in every manner regarding the project. Thank you

Enjoy the project 😋😋