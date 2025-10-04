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
| Project title                     | AI-Based Human Activity           |
|                                   | Recognition Using WiFi Channel    |
|                                   | State Information                 |
+-----------------------------------+-----------------------------------+
| Brief description of the research | **Background:**\                  |
| problem, aims, method and         | Accurate activity recognition     |
| expected outputs (100\~200 words) | plays an important role in smart  |
|                                   | home and healthcare systems,      |
|                                   | particularly in supporting        |
|                                   | independent living for older      |
|                                   | adults. For scenarios such as     |
|                                   | fall detection and daily activity |
|                                   | monitoring, WiFi Channel State    |
|                                   | Information (CSI) offers a        |
|                                   | low-cost, device-free, and        |
|                                   | privacy-conscious sensing         |
|                                   | approach. Compared to             |
|                                   | camera-based or wearable systems, |
|                                   | WiFi-based solutions are easier   |
|                                   | to deploy and generally better    |
|                                   | accepted by users.                |
|                                   |                                   |
|                                   | Despite its advantages, CSI-based |
|                                   | human activity recognition faces  |
|                                   | several technical hurdles.        |
|                                   | Existing public datasets are      |
|                                   | often limited in both scale and   |
|                                   | diversity, which restricts the    |
|                                   | generalizability of trained       |
|                                   | models. The presence of noise,    |
|                                   | multipath effects, and            |
|                                   | environmental changes further     |
|                                   | complicates real-time signal      |
|                                   | interpretation. In addition, many |
|                                   | prior studies rely on specific    |
|                                   | hardware setups, making wider     |
|                                   | adoption challenging. This        |
|                                   | project aims to address these     |
|                                   | limitations by applying data      |
|                                   | augmentation techniques,          |
|                                   | improving signal processing       |
|                                   | methods, and developing robust AI |
|                                   | models for activity recognition.  |
|                                   | The goal is to create a practical |
|                                   | and reliable solution that can    |
|                                   | operate effectively in real-world |
|                                   | indoor environments.              |
|                                   |                                   |
|                                   | **Objectives:**                   |
|                                   |                                   |
|                                   | 1.  Dataset Acquisition and       |
|                                   |     Augmentation：Review and      |
|                                   |     assess publicly available CSI |
|                                   |     datasets for human activity   |
|                                   |     recognition. If necessary,    |
|                                   |     collect additional data in    |
|                                   |     controlled environments.      |
|                                   |     Explore the use of generative |
|                                   |     models, such as GANs, to      |
|                                   |     expand the dataset and        |
|                                   |     improve coverage of activity  |
|                                   |     types and environmental       |
|                                   |     conditions.                   |
|                                   |                                   |
|                                   | 2.  Signal Processing and Feature |
|                                   |     Extraction: Develop           |
|                                   |     preprocessing methods to      |
|                                   |     improve the quality of CSI    |
|                                   |     signals, including noise      |
|                                   |     filtering, phase calibration, |
|                                   |     and subcarrier selection.     |
|                                   |     Apply time-frequency analysis |
|                                   |     to extract motion-relevant    |
|                                   |     features for classification   |
|                                   |     tasks.                        |
|                                   |                                   |
|                                   | 3.  Network Model Design: Design  |
|                                   |     and evaluate a range of       |
|                                   |     learning models---such as     |
|                                   |     convolutional, recurrent, or  |
|                                   |     transformer-based             |
|                                   |     architectures---for           |
|                                   |     recognizing human activities  |
|                                   |     from CSI data. Emphasis will  |
|                                   |     be placed on classification   |
|                                   |     accuracy and robustness       |
|                                   |     across different settings.    |
|                                   |                                   |
|                                   | 4.  System Evaluation: Test the   |
|                                   |     system's performance on       |
|                                   |     various activities, across    |
|                                   |     different physical            |
|                                   |     environments and user         |
|                                   |     profiles. Use                 |
|                                   |     cross-validation and live     |
|                                   |     trials to assess              |
|                                   |     generalization ability,       |
|                                   |     stability, and response       |
|                                   |     consistency.                  |
|                                   |                                   |
|                                   | 5.  Deployment Feasibility Study: |
|                                   |     Examine the practicality of   |
|                                   |     running the system in real    |
|                                   |     time using commonly available |
|                                   |     WiFi hardware, such as the    |
|                                   |     Intel 5300 NIC or low-cost    |
|                                   |     embedded platforms like       |
|                                   |     ESP32.                        |
|                                   |                                   |
|                                   | **Expected Outcomes:**            |
|                                   |                                   |
|                                   | A functional HAR prototype using  |
|                                   | CSI and AI models will be         |
|                                   | developed. The system will be     |
|                                   | tested with both real and         |
|                                   | synthetic data to evaluate        |
|                                   | accuracy, robustness, and         |
|                                   | response time. An augmented CSI   |
|                                   | dataset and benchmarking results  |
|                                   | across models and signal          |
|                                   | pipelines will also be delivered. |
|                                   | The project will demonstrate the  |
|                                   | feasibility of                    |
|                                   | privacy-preserving, non-intrusive |
|                                   | activity recognition using WiFi   |
|                                   | sensing, with potential for smart |
|                                   | home deployment.                  |
+-----------------------------------+-----------------------------------+
| Key words                         | -   Human Activity Recognition    |
|                                   |     (HAR)                         |
|                                   |                                   |
|                                   | -   WiFi Channel State            |
|                                   |     Information (CSI)             |
|                                   |                                   |
|                                   | -   Deep Learning                 |
|                                   |                                   |
|                                   | -   Signal Processing             |
|                                   |                                   |
|                                   | -   Fall Detection                |
|                                   |                                   |
|                                   | -   Generative Adversarial        |
|                                   |     Networks (GANs)               |
+-----------------------------------+-----------------------------------+
| Answerable research questions for | Research Questions:               |
| 3-5 students (desirable)          |                                   |
|                                   | -   How can generative models     |
|                                   |     improve the diversity and     |
|                                   |     quality of CSI datasets for   |
|                                   |     HAR?                          |
|                                   |                                   |
|                                   | -   What preprocessing techniques |
|                                   |     are most effective for        |
|                                   |     denoising and stabilizing CSI |
|                                   |     signals?                      |
|                                   |                                   |
|                                   | -   Which AI model architectures  |
|                                   |     yield the best performance    |
|                                   |     across different indoor       |
|                                   |     environments?                 |
|                                   |                                   |
|                                   | -   How well can models           |
|                                   |     generalize across subjects    |
|                                   |     and activity types?           |
|                                   |                                   |
|                                   | -   What is the feasibility of    |
|                                   |     running real-time CSI-based   |
|                                   |     HAR on edge devices?          |
+-----------------------------------+-----------------------------------+
| 3-5 key references (desirable)    | 1)  Wang, Y. et al. "DeepFi: Deep |
| and website resources             |     Learning for Indoor           |
|                                   |     Fingerprinting Using CSI."    |
|                                   |     WCNC, 2015.                   |
|                                   |                                   |
|                                   | 2)  Qian, Kun, et al. \"Widar:    |
|                                   |     Decimeter-level passive       |
|                                   |     tracking via velocity         |
|                                   |     monitoring with commodity     |
|                                   |     Wi-Fi.\" *Proceedings of the  |
|                                   |     18th ACM international        |
|                                   |     symposium on mobile ad hoc    |
|                                   |     networking and                |
|                                   |     computing*. 2017.             |
|                                   |                                   |
|                                   | 3)  Shi, Zhenguo, et al.          |
|                                   |     \"Environment-robust          |
|                                   |     device-free human activity    |
|                                   |     recognition with              |
|                                   |     channel-state-information     |
|                                   |     enhancement and one-shot      |
|                                   |     learning.\" *IEEE             |
|                                   |     Transactions on Mobile        |
|                                   |     Computing* 21.2 (2020):       |
|                                   |     540-554.                      |
|                                   |                                   |
|                                   | 4)  Shi, Zhenguo, et al.          |
|                                   |     \"Environment-robust          |
|                                   |     WiFi-based human activity     |
|                                   |     recognition using enhanced    |
|                                   |     CSI and deep learning.\" IEEE |
|                                   |     Internet of Things Journal    |
|                                   |     9.24 (2022): 24643-24654.     |
|                                   |                                   |
|                                   | 5)  Mao, Yimin, et al. \"Wi-Cro:  |
|                                   |     WiFi-based Cross Domain       |
|                                   |     Activity Recognition via      |
|                                   |     Modified GAN.\" *IEEE         |
|                                   |     Transactions on Vehicular     |
|                                   |     Technology* (2024).           |
+-----------------------------------+-----------------------------------+
| Required major of studies,        | Software development and computer |
| desirable skill sets, knowledge,  | science majors. It is desirable   |
| and speciality                    | if students have or willing to    |
|                                   | develop skills in the following   |
|                                   | areas:                            |
|                                   |                                   |
|                                   | -   Familiarity with deep         |
|                                   |     learning (PyTorch,            |
|                                   |     TensorFlow)                   |
|                                   |                                   |
|                                   | -   Background in wireless        |
|                                   |     networks and signal           |
|                                   |     processing                    |
|                                   |                                   |
|                                   | -   Experience with GANs or data  |
|                                   |     augmentation techniques       |
|                                   |                                   |
|                                   | -   Practical skills in data      |
|                                   |     collection, preprocessing,    |
|                                   |     and model training            |
|                                   |                                   |
|                                   | -   Understanding of WiFi CSI     |
|                                   |     tools (e.g., Intel 5300 CSI   |
|                                   |     Tool, Nexmon, ESP32 SDK)      |
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
| Remarks on conditions of offer    |                                   |
+-----------------------------------+-----------------------------------+
