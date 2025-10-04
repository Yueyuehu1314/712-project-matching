IFN712 Research Project Proposal-Form

(Submitted to <y.feng@qut.edu.au> by 30 June 2025)

+-----------------------------------+-----------------------------------+
| Project agency (school, industry) | School of Computer Science        |
+===================================+===================================+
| Industry supervisor and contact   | Wenzong Gao,                      |
| emails                            | wenzong.gao\@kurloo.io            |
+-----------------------------------+-----------------------------------+
| Academic Supervisor name(s) and   | Yanming Feng, y.feng\@qut.edu.au  |
| contact emails                    |                                   |
+-----------------------------------+-----------------------------------+
| Information Technology major(s)   | Data Science and Computer Science |
+-----------------------------------+-----------------------------------+
| Project title                     | Machine Learning-Based Prediction |
|                                   | of GNSS Precise Ephemeris Using   |
|                                   | Broadcast Orbit Data              |
+-----------------------------------+-----------------------------------+
| Brief description of the research | The Global Navigation Satellite   |
| problem, gaps, aims, methodology  | Systems (GNSS), particularly the  |
| and expected outputs (\~200       | US\'s Global Positioning System   |
| words)                            | (GPS), have become integral to    |
|                                   | daily life, industry, military    |
|                                   | operations, and scientific        |
|                                   | research. GNSS works by letting   |
|                                   | users calculate their position    |
|                                   | based on signals from satellites. |
|                                   | Each satellite sends out its      |
|                                   | predicted position---called the   |
|                                   | broadcast ephemeris---which your  |
|                                   | navigation device uses to figure  |
|                                   | out where the satellite is. These |
|                                   | broadcast orbits are calculated   |
|                                   | in advance and transmitted in     |
|                                   | real time, but their precision is |
|                                   | limited. Typically, the error in  |
|                                   | broadcast orbits is about 1--2    |
|                                   | meters, and sometimes even        |
|                                   | greater, due to various           |
|                                   | unpredictable factors affecting   |
|                                   | satellites in space.              |
|                                   |                                   |
|                                   | In contrast, after the fact,      |
|                                   | international agencies (such as   |
|                                   | the International GNSS Service)   |
|                                   | process vast amounts of tracking  |
|                                   | data to produce the precise       |
|                                   | ephemeris. These precise orbits   |
|                                   | show where the satellites         |
|                                   | actually were and are accurate to |
|                                   | just 2--5 centimetres. However,   |
|                                   | they become available only        |
|                                   | several hours to a day later, so  |
|                                   | they cannot help in real-time     |
|                                   | positioning.                      |
|                                   |                                   |
|                                   | This project aims to use Machine  |
|                                   | Learning (ML) to bridge this gap. |
|                                   | By collecting historical pairs of |
|                                   | broadcast and precise ephemeris   |
|                                   | data, we will train ML models to  |
|                                   | predict the difference (the       |
|                                   | error) between the real-time      |
|                                   | broadcast and the delayed precise |
|                                   | orbit. The ML model will take the |
|                                   | broadcast ephemeris as input and  |
|                                   | output the estimated correction   |
|                                   | needed to approach precise-orbit  |
|                                   | accuracy. This approach can       |
|                                   | potentially provide real-time     |
|                                   | corrections for navigation,       |
|                                   | making everyday positioning more  |
|                                   | accurate.                         |
|                                   |                                   |
|                                   | Expected outputs include:         |
|                                   |                                   |
|                                   | -   A proof-of-concept ML model   |
|                                   |     for near-real-time GPS orbit  |
|                                   |     correction                    |
|                                   |                                   |
|                                   | -   Quantitative evaluation of    |
|                                   |     the accuracy improvement      |
|                                   |                                   |
|                                   | -   Open-source code and a        |
|                                   |     reproducible workflow for     |
|                                   |     further research              |
+-----------------------------------+-----------------------------------+
| Answerable research questions for | -   How do errors between         |
| 3-5 students                      |     broadcast and precise GPS     |
|                                   |     ephemerides evolve over time  |
|                                   |     and what factors influence    |
|                                   |     them?                         |
|                                   |                                   |
|                                   | -   What features from broadcast  |
|                                   |     ephemeris are most useful for |
|                                   |     predicting the error between  |
|                                   |     broadcast and precise orbits? |
|                                   |                                   |
|                                   | -   How do different ML models    |
|                                   |     (regression, tree-based,      |
|                                   |     neural networks) perform in   |
|                                   |     predicting orbit corrections? |
|                                   |                                   |
|                                   | -   How much can the accuracy of  |
|                                   |     user positioning be improved  |
|                                   |     by applying the ML-based      |
|                                   |     corrections?                  |
|                                   |                                   |
|                                   | -   How robust is the ML-based    |
|                                   |     correction approach to        |
|                                   |     missing data or outliers in   |
|                                   |     the input?                    |
+-----------------------------------+-----------------------------------+
| 3-5 key references (very          | -   IGS Products:                 |
| preferable for students to start) |     <https://igs.org/products/>   |
|                                   |                                   |
|                                   | -   Kouba, J., & Héroux, P.       |
|                                   |     (2001). Precise point         |
|                                   |     positioning using IGS orbit   |
|                                   |     and clock products. *GPS      |
|                                   |     solutions*, *5*, 12-28.       |
|                                   |                                   |
|                                   | -   Griffiths, J., & Ray, J. R.   |
|                                   |     (2009). On the precision and  |
|                                   |     accuracy of IGS               |
|                                   |     orbits. *Journal of           |
|                                   |     Geodesy*, *83*(3), 277-287.   |
|                                   |                                   |
|                                   | -   Springer Handbook of Global   |
|                                   |     Navigation Satellite Systems. |
|                                   |     (2017).                       |
|                                   |     <https://doi.org/10.1007/978- |
|                                   | 3-319-42928-1>                    |
|                                   |     (Chapter 2)                   |
+-----------------------------------+-----------------------------------+
| Required major of studies,        | Students majoring data science    |
| skills, knowledge, and speciality | and computer science can          |
|                                   | participate in the project.       |
|                                   |                                   |
|                                   | Programming skills (Python or     |
|                                   | Matlab)                           |
|                                   |                                   |
|                                   | Experience with machine learning  |
|                                   | frameworks                        |
+-----------------------------------+-----------------------------------+
| **Industry-based project: Student | ☐ Project IP vests in the Student |
| IP Agreement.** This is the IP    | with a license back to Industry   |
| model agreed between the parties. | Partner **(license)**             |
| Please note that it is QUT policy |                                   |
| that where possible students      | OR                                |
| should be allowed to keep their   |                                   |
| IP. If students are asked to      | ☐ Project IP vests in the         |
| assign their work then please     | Industry Partner with a licence   |
| **provide a brief rationale** as  | back to the Student               |
| additional permissions are needed | **(assignment)**                  |
| by QUT to approve.                |                                   |
|                                   | OR                                |
|                                   |                                   |
|                                   | ☒ Academic project                |
+-----------------------------------+-----------------------------------+
| Number of students                | 3-5                               |
+-----------------------------------+-----------------------------------+
| Student names (if known)          |                                   |
+-----------------------------------+-----------------------------------+
| 1                                 |                                   |
+-----------------------------------+-----------------------------------+
| 2                                 |                                   |
+-----------------------------------+-----------------------------------+
| 3                                 |                                   |
+-----------------------------------+-----------------------------------+
| 4                                 |                                   |
+-----------------------------------+-----------------------------------+
| 5                                 |                                   |
+-----------------------------------+-----------------------------------+
| Remarks on conditions of offer    | The supervising team will         |
|                                   | shortlist the candidates after    |
|                                   | their application.                |
+-----------------------------------+-----------------------------------+
