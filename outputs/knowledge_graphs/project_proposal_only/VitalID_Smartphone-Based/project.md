IFN712 Research Project Form

(Submitted to <y.feng@qut.edu.au> by 30 June 2025)

+-----------------------------------+-----------------------------------+
| Project agency (school, industry, | School of Computer Science/NRSAG  |
| )                                 | project                           |
+===================================+===================================+
| Industry/project supervisor and   |                                   |
| contact emails                    |                                   |
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
| Project title                     | VitalID: Smartphone-Based         |
|                                   | Identity Authentication Using     |
|                                   | Heart Rate and Breathing Signals  |
+-----------------------------------+-----------------------------------+
| Brief description of the research | **Background:**\                  |
| problem, aims, method and         | User authentication plays a       |
| expected outputs (100\~200 words) | critical role in mobile security  |
|                                   | and personalized device access.   |
|                                   | While fingerprint and facial      |
|                                   | recognition are widely adopted,   |
|                                   | they are not ideal in all         |
|                                   | scenarios---such as when a user's |
|                                   | hands are wet or face is covered. |
|                                   | Furthermore, these modalities     |
|                                   | require explicit interaction and  |
|                                   | involve sensitive biometric data  |
|                                   | that cannot be changed once       |
|                                   | leaked.                           |
|                                   |                                   |
|                                   | Vital signs, including heart rate |
|                                   | and breathing patterns, reflect   |
|                                   | physiological characteristics     |
|                                   | unique to each person and are     |
|                                   | difficult to forge.               |
|                                   | Photoplethysmography (PPG),       |
|                                   | obtainable through a smartphone   |
|                                   | camera and flashlight, allows     |
|                                   | measurement of heart rate and     |
|                                   | heart rate variability (HRV).     |
|                                   | Meanwhile, breathing sounds       |
|                                   | captured using the microphone     |
|                                   | contain frequency and rhythm      |
|                                   | patterns that can serve as        |
|                                   | auxiliary biometric signals. This |
|                                   | project investigates the          |
|                                   | feasibility of combining PPG and  |
|                                   | breathing signals for identity    |
|                                   | verification in a non-intrusive   |
|                                   | and device-friendly way.          |
|                                   |                                   |
|                                   | **Objectives:**                   |
|                                   |                                   |
|                                   | 1.  Vital Sign Data Acquisition:  |
|                                   |     Develop a smartphone-based    |
|                                   |     system to collect PPG signals |
|                                   |     using the camera and          |
|                                   |     flashlight, and capture       |
|                                   |     breathing sounds using the    |
|                                   |     built-in microphone.          |
|                                   |                                   |
|                                   | 2.  Signal Preprocessing and      |
|                                   |     Feature Extraction: Process   |
|                                   |     PPG data to extract heart     |
|                                   |     rate and HRV features. Apply  |
|                                   |     audio filtering and transform |
|                                   |     techniques to extract         |
|                                   |     breathing-related features.   |
|                                   |                                   |
|                                   | 3.  Model Design and Training:    |
|                                   |     Construct and train a deep    |
|                                   |     learning model (e.g., CNN or  |
|                                   |     Siamese Network) that learns  |
|                                   |     to identify individuals based |
|                                   |     on combined vital sign        |
|                                   |     features.                     |
|                                   |                                   |
|                                   | 4.  Prototype Development: Build  |
|                                   |     a functional Android          |
|                                   |     prototype with an intuitive   |
|                                   |     interface to perform          |
|                                   |     real-time recording and       |
|                                   |     authentication on-device.     |
|                                   |                                   |
|                                   | 5.  Evaluation and Performance    |
|                                   |     Analysis: Evaluate the system |
|                                   |     in terms of authentication    |
|                                   |     accuracy, false               |
|                                   |     acceptance/rejection rates,   |
|                                   |     signal robustness under       |
|                                   |     different user and            |
|                                   |     environmental conditions, and |
|                                   |     usability.                    |
|                                   |                                   |
|                                   | **Expected Outcomes:**            |
|                                   |                                   |
|                                   | The project will produce a        |
|                                   | complete prototype system that    |
|                                   | enables contactless identity      |
|                                   | authentication using              |
|                                   | smartphone-acquired physiological |
|                                   | signals. It will include a mobile |
|                                   | interface for data collection and |
|                                   | real-time feedback, signal        |
|                                   | processing modules, and a trained |
|                                   | deep learning model. The system   |
|                                   | will be tested on a small user    |
|                                   | dataset to assess accuracy and    |
|                                   | reliability. Results will inform  |
|                                   | future development of             |
|                                   | lightweight, privacy-conscious    |
|                                   | biometric systems for mobile and  |
|                                   | IoT platforms.                    |
+-----------------------------------+-----------------------------------+
| Key words                         | -   Vital Signs Authentication    |
|                                   |                                   |
|                                   | -   Smartphone Sensors            |
|                                   |                                   |
|                                   | -   Photoplethysmography (PPG)    |
|                                   |                                   |
|                                   | -   Heart Rate Variability (HRV)  |
|                                   |                                   |
|                                   | -   Breathing Audio               |
|                                   |                                   |
|                                   | -   Deep learning                 |
|                                   |                                   |
|                                   | -   Multimodal Biometrics         |
+-----------------------------------+-----------------------------------+
| Answerable research questions for | Research Questions:               |
| 3-5 students (desirable)          |                                   |
|                                   | -   How distinctive and stable    |
|                                   |     are heart rate and HRV        |
|                                   |     signals for individual        |
|                                   |     identification across time    |
|                                   |     and states?                   |
|                                   |                                   |
|                                   | -   Can breathing sounds serve as |
|                                   |     a complementary biometric     |
|                                   |     feature in a smartphone-based |
|                                   |     system?                       |
|                                   |                                   |
|                                   | -   What preprocessing techniques |
|                                   |     are most effective for        |
|                                   |     low-noise PPG and audio       |
|                                   |     signal extraction using       |
|                                   |     built-in smartphone sensors?  |
|                                   |                                   |
|                                   | -   How do deep learning models   |
|                                   |     perform on vital sign-based   |
|                                   |     authentication tasks under    |
|                                   |     varying conditions (e.g.,     |
|                                   |     lighting, background noise)?  |
|                                   |                                   |
|                                   | -   What is the minimum recording |
|                                   |     duration required for         |
|                                   |     reliable authentication?      |
+-----------------------------------+-----------------------------------+
| 3-5 key references (desirable)    | 1)  Hussain, S. et al.            |
| and website resources             |     "BreathPrint: Breathing       |
|                                   |     Acoustic Authentication Using |
|                                   |     Smartphones." IEEE            |
|                                   |     Access, 2020.                 |
|                                   |                                   |
|                                   | 2)  Zhang, Y. et al. "PPG-based   |
|                                   |     Biometric Authentication for  |
|                                   |     Mobile Devices." ACM          |
|                                   |     CCS, 2016.                    |
|                                   |                                   |
|                                   | 3)  Wang, T. et al. "Smartphone   |
|                                   |     PPG and Deep Learning for     |
|                                   |     Biometric Identification."    |
|                                   |     Sensors, 2022.                |
|                                   |                                   |
|                                   | 4)  Hossain, M. et al. "Vital     |
|                                   |     Signs Based Biometric         |
|                                   |     Authentication: A Review."    |
|                                   |     Sensors, 2022.                |
|                                   |                                   |
|                                   | 5)  Librosa: Audio Analysis in    |
|                                   |     Python -- https://librosa.org |
+-----------------------------------+-----------------------------------+
| Required major of studies,        | Software development and computer |
| desirable skill sets, knowledge,  | science majors. It is desirable   |
| and speciality                    | if students have or willing to    |
|                                   | develop skills in the following   |
|                                   | areas:                            |
|                                   |                                   |
|                                   | -   Android programming or        |
|                                   |     collecting sensor data on     |
|                                   |     smartphones                   |
|                                   |                                   |
|                                   | -   Digital signal processing for |
|                                   |     physiological signals such as |
|                                   |     PPG and audio                 |
|                                   |                                   |
|                                   | -   Machine learning using        |
|                                   |     frameworks such as PyTorch or |
|                                   |     TensorFlow                    |
|                                   |                                   |
|                                   | -   Understanding of biometric    |
|                                   |     authentication systems or     |
|                                   |     vital sign analysis           |
|                                   |                                   |
|                                   | -   Practical experience in       |
|                                   |     mobile UI/UX design, system   |
|                                   |     testing, and real-time        |
|                                   |     integration                   |
+-----------------------------------+-----------------------------------+
| > **Industry-based project:       | ☐ Project IP vests in the student |
| > Student IP Agreement.** This is | with a license back to Industry   |
| > the IP model agreed between the | Partner **(licence)**             |
| > parties. Please note that it is |                                   |
| > QUT policy that where possible  | OR                                |
| > students should be allowed to   |                                   |
| > keep their IP. If students are  | ☐ Project IP vests in the         |
| > asked to assign their work,     | Industry Partner/Project owner    |
| > then please **provide a brief   | with a licence back to the        |
| > rationale** as additional       | student **(assignment)**          |
| > permissions are needed by QUT   |                                   |
| > to approve.                     | OR                                |
|                                   |                                   |
|                                   | ☒ Academic project (No IP         |
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
