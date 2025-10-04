IFN712 Research Project Form

(Submitted to <y.feng@qut.edu.au> by 30 June 2025)

+-----------------------------------+-----------------------------------+
| Project agency (school, industry, | School of Computer Science/NRSAG  |
| )                                 | project                           |
+===================================+===================================+
| Industry/project supervisor and   | Dr Zhenguo Shi,                   |
| contact emails                    | <zhenguo.shi@qut.edu.au>          |
+-----------------------------------+-----------------------------------+
| Academic Supervisor name(s) and   | Yanming Feng <y.feng@qut.edu.au>, |
| contact emails                    |                                   |
|                                   | Zhenguo Shi,                      |
|                                   | <zhenguo.shi@qut.edu.au>          |
+-----------------------------------+-----------------------------------+
| Information Technology major(s)   | Software Development, Computer    |
|                                   | Science and Data Science,         |
|                                   | Networks and cybersecurity        |
+-----------------------------------+-----------------------------------+
| Project title                     | Smart Intersection Localization   |
|                                   | for Pedestrians Using Bluetooth   |
|                                   | and Deep learning                 |
+-----------------------------------+-----------------------------------+
| Brief description of the research | **Background:**\                  |
| problem, aims, method and         | Vulnerable Road Users (VRUs),     |
| expected outputs (100\~200 words) | such as pedestrians, cyclists,    |
|                                   | and scooter riders, are at        |
|                                   | greater risk of accidents at      |
|                                   | signalized intersections due to   |
|                                   | limited line of sight and slower  |
|                                   | reaction times from drivers.      |
|                                   | While camera and LiDAR-based      |
|                                   | detection systems have been used  |
|                                   | to improve safety, these          |
|                                   | solutions are often expensive,    |
|                                   | require complex infrastructure,   |
|                                   | and raise privacy concerns. In    |
|                                   | contrast, Bluetooth Low Energy    |
|                                   | (BLE) technology offers a         |
|                                   | low-cost and privacy-friendly     |
|                                   | alternative for short-range       |
|                                   | localization. However, RSSI-based |
|                                   | positioning with BLE is known to  |
|                                   | suffer from signal fluctuations   |
|                                   | caused by multipath effects,      |
|                                   | obstructions, and environmental   |
|                                   | variability. This project         |
|                                   | addresses these challenges by     |
|                                   | building a real-time VRU          |
|                                   | positioning system using multiple |
|                                   | BLE locators based on the nRF5340 |
|                                   | platform. By applying deep        |
|                                   | learning methods such as LSTM and |
|                                   | CNN, the system aims to improve   |
|                                   | the stability and accuracy of     |
|                                   | RSSI-based localization.          |
|                                   | Performance will be evaluated in  |
|                                   | both lab and semi-field settings  |
|                                   | to assess its suitability for     |
|                                   | real-world deployment in smart    |
|                                   | transport infrastructure.         |
|                                   |                                   |
|                                   | **Objectives:**                   |
|                                   |                                   |
|                                   | 1.  RSSI Data Collection: Deploy  |
|                                   |     multiple nRF5340-based BLE    |
|                                   |     devices at a simulated        |
|                                   |     intersection to collect RSSI  |
|                                   |     readings from VRUs under      |
|                                   |     different conditions,         |
|                                   |     including obstructed and      |
|                                   |     unobstructed paths.           |
|                                   |                                   |
|                                   | 2.  Localization Model            |
|                                   |     Development: Build and train  |
|                                   |     deep learning models, such as |
|                                   |     LSTM, BiLSTM, or CNN, to      |
|                                   |     estimate the position of VRUs |
|                                   |     using sequences of RSSI data, |
|                                   |     with a focus on improving     |
|                                   |     accuracy and consistency.     |
|                                   |                                   |
|                                   | 3.  Signal Preprocessing and      |
|                                   |     Feature Extraction: Apply     |
|                                   |     filtering, smoothing, and     |
|                                   |     statistical feature           |
|                                   |     extraction techniques to the  |
|                                   |     raw RSSI data to reduce noise |
|                                   |     and support robust model      |
|                                   |     training across varying       |
|                                   |     environments.                 |
|                                   |                                   |
|                                   | 4.  System Integration: Combine   |
|                                   |     BLE broadcasting, RSSI        |
|                                   |     acquisition, and model        |
|                                   |     inference into a single       |
|                                   |     positioning system capable of |
|                                   |     running in real time.         |
|                                   |                                   |
|                                   | 5.  Performance Evaluation and    |
|                                   |     Validation: Test the system   |
|                                   |     in lab and semi-field         |
|                                   |     conditions to evaluate        |
|                                   |     positioning accuracy,         |
|                                   |     latency, and reliability, and |
|                                   |     assess its potential for      |
|                                   |     deployment at real-world      |
|                                   |     intersections.                |
|                                   |                                   |
|                                   | **Expected Outcomes:**            |
|                                   |                                   |
|                                   | The project will deliver a        |
|                                   | functional prototype that         |
|                                   | demonstrates RSSI-based           |
|                                   | localization using nRF5340        |
|                                   | Bluetooth devices and deep        |
|                                   | learning techniques. The system   |
|                                   | will be tested under controlled   |
|                                   | and semi-field conditions to      |
|                                   | evaluate positioning accuracy,    |
|                                   | robustness, and latency.          |
|                                   | Comparative analysis will be      |
|                                   | conducted between traditional     |
|                                   | trilateration methods and         |
|                                   | learning-based approaches to      |
|                                   | assess performance gains. The     |
|                                   | outcome is expected to provide a  |
|                                   | practical, low-cost, and          |
|                                   | privacy-conscious solution for    |
|                                   | detecting VRU locations at        |
|                                   | intersections, offering a         |
|                                   | potential path toward real-world  |
|                                   | deployment in intelligent         |
|                                   | transport systems.                |
+-----------------------------------+-----------------------------------+
| Key words                         | -   Bluetooth RSSI Localization   |
|                                   |                                   |
|                                   | -   Vulnerable Road User (VRU)    |
|                                   |                                   |
|                                   | -   Deep Learning for Positioning |
|                                   |                                   |
|                                   | -   Intersection Safety Systems   |
|                                   |                                   |
|                                   | -   Noise-Robust RSSI Estimation  |
+-----------------------------------+-----------------------------------+
| Answerable research questions for | Research Questions:               |
| 3-5 students (desirable)          |                                   |
|                                   | -   How can deep learning models  |
|                                   |     mitigate the noise and        |
|                                   |     instability of Bluetooth RSSI |
|                                   |     signals for accurate          |
|                                   |     real-time localization?       |
|                                   |                                   |
|                                   | -   What is the trade-off between |
|                                   |     number of beacons and         |
|                                   |     positioning accuracy in the   |
|                                   |     BLE-based intersection setup? |
|                                   |                                   |
|                                   | -   Which neural network          |
|                                   |     architecture (e.g., CNN vs.   |
|                                   |     LSTM) performs best for       |
|                                   |     time-series RSSI              |
|                                   |     localization?                 |
|                                   |                                   |
|                                   | -   How does the positioning      |
|                                   |     performance degrade in        |
|                                   |     high-multipath environments   |
|                                   |     or when BLE devices are       |
|                                   |     moving?                       |
|                                   |                                   |
|                                   | -   Can we generalize the trained |
|                                   |     model across different        |
|                                   |     intersection geometries?      |
+-----------------------------------+-----------------------------------+
| 3-5 key references (desirable)    | 1)  Faragher, R. & Harle, R.      |
| and website resources             |     "Location Fingerprinting With |
|                                   |     Bluetooth Low Energy          |
|                                   |     Beacons." IEEE Journal on     |
|                                   |     Selected Areas in             |
|                                   |     Communications, 2015.         |
|                                   |                                   |
|                                   | 2)  nRF5340 Bluetooth Direction   |
|                                   |     Finding Development Kit.      |
|                                   |     <https://www.nordicsemi.com/P |
|                                   | roducts/nRF5340>                  |
|                                   |                                   |
|                                   | 3)  Matlab. Bluetooth LE          |
|                                   |     Positioning with Deep         |
|                                   |     Learning.                     |
|                                   |     https://au.mathworks.com/help |
|                                   | /bluetooth/ug/bluetooth-le-positi |
|                                   | oning-with-deep-learning.html     |
|                                   |                                   |
|                                   | 4)  Wang, Y. et al. "DeepFi: Deep |
|                                   |     Learning for Indoor           |
|                                   |     Fingerprinting Using Channel  |
|                                   |     State Information."           |
|                                   |     WCNC, 2015.                   |
|                                   |                                   |
|                                   | 5)  Zafari, F., Gkelias, A., &    |
|                                   |     Leung, K.K. "A Survey of      |
|                                   |     Indoor Localization Systems   |
|                                   |     and Technologies." IEEE       |
|                                   |     Communications Surveys &      |
|                                   |     Tutorials, 2019.              |
+-----------------------------------+-----------------------------------+
| Required major of studies,        | Software development and computer |
| desirable skill sets, knowledge,  | science majors. It is desirable   |
| and speciality                    | if students have or willing to    |
|                                   | develop skills in the following   |
|                                   | areas:                            |
|                                   |                                   |
|                                   | -   Embedded C/C++ or Zephyr RTOS |
|                                   |     development.                  |
|                                   |                                   |
|                                   | -   Python and deep learning      |
|                                   |     frameworks (e.g., PyTorch or  |
|                                   |     TensorFlow)                   |
|                                   |                                   |
|                                   | -   It is desirable if students   |
|                                   |     have some background in data  |
|                                   |     processing and Bluetooth      |
|                                   |     RSSI-based localization       |
|                                   |     algorithms.Experience with    |
|                                   |     real-time data collection and |
|                                   |     MQTT or serial data protocols |
|                                   |                                   |
|                                   | -   Strong hands-on skills in     |
|                                   |     setting up experiments,       |
|                                   |     troubleshooting embedded      |
|                                   |     systems, and evaluating       |
|                                   |     system performance in         |
|                                   |     real-world scenarios.         |
+-----------------------------------+-----------------------------------+
| > **Industry-based project:       | ☐ Project IP vests in the student |
| > Student IP Agreement.** This is | with a license back to Industry   |
| > the IP model agreed between the | Partner **(licence)**             |
| > parties. Please note that it is |                                   |
| > QUT policy that where possible  | OR                                |
| > students should be allowed to   |                                   |
| > keep their IP. If students are  | ☒ Project IP vests in the         |
| > asked to assign their work,     | Industry Partner/Project owner    |
| > then please **provide a brief   | with a licence back to the        |
| > rationale** as additional       | student **(assignment)**          |
| > permissions are needed by QUT   |                                   |
| > to approve.                     | OR                                |
|                                   |                                   |
|                                   | ☐ Academic project (No IP         |
|                                   | agreement needed)                 |
+-----------------------------------+-----------------------------------+
| Number of students                | 5                                 |
+-----------------------------------+-----------------------------------+
| The message from supervisor(s)    |                                   |
| about the acceptance for this     |                                   |
| project                           |                                   |
+-----------------------------------+-----------------------------------+
| Student name(s)                   |                                   |
|                                   |                                   |
| (Print your name and submit this  |                                   |
| form by the end of Week 2)        |                                   |
+-----------------------------------+-----------------------------------+
| Date                              |                                   |
+-----------------------------------+-----------------------------------+
| Remarks on conditions of offer    | This research is conducted as     |
|                                   | part of a government-funded       |
|                                   | project. Participating students   |
|                                   | will be required to sign an       |
|                                   | Intellectual Property (IP)        |
|                                   | agreement with the QUT project    |
|                                   | owners. The supervising team will |
|                                   | shortlist candidates following    |
|                                   | the application process.          |
+-----------------------------------+-----------------------------------+
