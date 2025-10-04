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
| Project title                     | Testing and Validating the Impact |
|                                   | of GNSS Signal Obstruction on     |
|                                   | Positioning Accuracy              |
+-----------------------------------+-----------------------------------+
| Brief description of the research | Global Navigation Satellite       |
| problem, gaps, aims, methodology  | Systems (GNSS), such as GPS, are  |
| and expected outputs (\~200       | essential for accurate            |
| words)                            | positioning in a wide range of    |
|                                   | applications. In real-world       |
|                                   | environments, GNSS receivers are  |
|                                   | often deployed in locations where |
|                                   | satellite signals may be blocked  |
|                                   | or degraded by obstacles such as  |
|                                   | buildings, trees, or other        |
|                                   | structures. These obstructions    |
|                                   | can cause signal loss, multipath  |
|                                   | effects, and ultimately reduce    |
|                                   | the accuracy and precision of     |
|                                   | GNSS-based positioning.           |
|                                   |                                   |
|                                   | This project aims to              |
|                                   | systematically evaluate how       |
|                                   | signal obstructions impact the    |
|                                   | precision of GNSS positioning. In |
|                                   | our setup, multiple GNSS          |
|                                   | receivers have been installed in  |
|                                   | environments with varying degrees |
|                                   | of obstruction. Some receivers    |
|                                   | experience clear sky visibility,  |
|                                   | while others are partially or     |
|                                   | heavily blocked by surrounding    |
|                                   | obstacles.                        |
|                                   |                                   |
|                                   | The proposed methodology involves |
|                                   | identifying and removing GNSS     |
|                                   | satellite signals that are        |
|                                   | affected by these                 |
|                                   | obstacles---typically those       |
|                                   | arriving from certain azimuth     |
|                                   | (direction) and elevation (angle  |
|                                   | above the horizon) ranges. By     |
|                                   | processing the GNSS data both     |
|                                   | with and without these obstructed |
|                                   | signals, the project will         |
|                                   | quantify the resulting changes in |
|                                   | positioning accuracy and          |
|                                   | precision. This approach allows   |
|                                   | for a controlled analysis of how  |
|                                   | different types and degrees of    |
|                                   | signal blockage impact            |
|                                   | positioning results.              |
|                                   |                                   |
|                                   | Expected outcomes include a       |
|                                   | reproducible method for filtering |
|                                   | obstructed signals, quantitative  |
|                                   | assessments of precision          |
|                                   | degradation due to obstacles, and |
|                                   | practical recommendations for     |
|                                   | optimizing GNSS receiver          |
|                                   | placement and data quality in     |
|                                   | challenging environments.         |
+-----------------------------------+-----------------------------------+
| Answerable research questions for | -   How does simulated removal of |
| 3-5 students                      |     GNSS signals from certain     |
|                                   |     azimuth and elevation ranges  |
|                                   |     impact positioning accuracy   |
|                                   |     and precision?                |
|                                   |                                   |
|                                   | -   How do the effects of signal  |
|                                   |     obstruction vary across       |
|                                   |     different datasets and        |
|                                   |     environmental conditions?     |
|                                   |                                   |
|                                   | -   What are the minimum sky      |
|                                   |     visibility requirements for   |
|                                   |     maintaining acceptable GNSS   |
|                                   |     positioning accuracy in       |
|                                   |     obstructed areas?             |
|                                   |                                   |
|                                   | -   What strategies can be        |
|                                   |     recommended for GNSS data     |
|                                   |     quality control and receiver  |
|                                   |     deployment in challenging     |
|                                   |     environments?                 |
+-----------------------------------+-----------------------------------+
| 3-5 key references (very          | -    RTKLIB manual                |
| preferable for students to start) |     (http://www.rtklib.com/prog/m |
|                                   | anual\_2.4.2.pdf)                 |
|                                   |                                   |
|                                   | -   Langley, R. B. (1999).        |
|                                   |     Dilution of precision. *GPS   |
|                                   |     world*, *10*(5), 52-59.       |
|                                   |                                   |
|                                   | -   Hussain, A., Akhtar, F.,      |
|                                   |     Khand, Z. H., Rajput, A., &   |
|                                   |     Shaukat, Z. (2021).           |
|                                   |     Complexity and limitations of |
|                                   |     GNSS signal reception in      |
|                                   |     highly obstructed             |
|                                   |     enviroments. *Engineering,    |
|                                   |     Technology & Applied Science  |
|                                   |     Research*, *11*(2),           |
|                                   |     6864-6868.                    |
|                                   |                                   |
|                                   | -   Springer Handbook of Global   |
|                                   |     Navigation Satellite Systems. |
|                                   |     (2017).                       |
|                                   |     <https://doi.org/10.1007/978- |
|                                   | 3-319-42928-1>                    |
+-----------------------------------+-----------------------------------+
| Required major of studies,        | Students majoring data science    |
| skills, knowledge, and speciality | and computer science can          |
|                                   | participate in the project.       |
|                                   |                                   |
|                                   | Programming skills (Python or     |
|                                   | Matlab)                           |
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
