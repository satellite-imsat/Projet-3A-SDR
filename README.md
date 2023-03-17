# Projet-3A-SDR

Auteurs :
* Thomas Aussaguès
* Arthur Docquois
* Aurélien Gossse 
* Selman Sezguin

<CENTER>
<font size="3"> Contact : <a href="mailto:arthur.docquois@imt-atlantique.net@example.com">{name.surname}@imt-atlantique.net</a></font></p>
</CENTER>

## Installation de la partie STM32

### Cette partie s'adresse aux personnes voulant importer le projet sur carte STM32F407G. 
Dans un premier temps, démarrez le projet sur STM32CubeIDE en partant du code example ST qui utilise les librairies USB : FatFs_USBDisk. Localisez aussi son emplacement sur votre disque.

Une fois le projet crée, remplacez le dossier User par celui du dépôt. 
Ajoutez le dossier librtlsdr dans le dossier middlewares du projet.
Remplacez le fichier usbh_diskio_dma.h, se trouvant dans Middlewares/FatFs/Drivers par celui présent dans le dépôt. 

Allez à l'emplacement du dossier example FatFs_USBDisk, dans le dossier Inc, remplacez tous les fichiers présents par les fichiers du dossier Inc du dépôt.

Finalement, nous allons inclure dans le compilateur les librairies à ajouter. Clic droit sur le projet > Properties > C/C++ build > Settings > MCU GCC Compiler > include paths. Ajoutez-y les dossiers librtlsdr de Middlewares et usb de User. Vous devriez obtenir la configuration suivante : 

<CENTER>
<img src="images/STM32Cube-includeLibrairies.PNG" width="800"/>
</CENTER>
L'ajout de la trace dans les includes n'est pas obligatoire. 

## Installation de la partie ```python```

### Cette partie s'adresse aux personnes désirant effectuer des simulations d'émission & réception de signaux AIS en python

Dans ce projet, les développements ```python``` ont été effectués avec ```python```  3.10.9.

1) Créer un nouvel environnment ```python``` à partir du fichier ```requirements.txt```.
2) Pour tester l'architecture sur des sigaux réels, fournis dans le dossier ```python/ais_data```, lancer le script ```demo_real_ais.py```. Les résultats attendus sont les suivants :

- Message Type    : 1
- MMSI            : 305323000
- Longitude (deg) : -6.233335
- Latitude (deg)  : 47.996025
- Course (deg)    : 25.3
- CRC             : not correct

3. Pour simuler les performances de l'architecture proposée, exécuter les scripts ```demo_per_demodulator.py```& ```demo_perf_decoder.py```.

Ce projet a été réalisé dans le cadre de l'UE ProCom proposé par IMT Atlantique en collaboration avec le club satellite de l'école, IMSAT.

<CENTER>
<p float="center">
  <img
src="https://www.imt-atlantique.fr/sites/default/files/Images/Ecole/charte-graphique/IMT_Atlantique_logo_RVB_Baseline_400x272.jpg"
WIDTH=300 HEIGHT=200>
  <img
src="https://avatars.githubusercontent.com/u/93446255?s=200&v=4"
WIDTH=200 HEIGHT=200>
</p>
</CENTER>
