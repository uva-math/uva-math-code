---
title: Research areas
layout: g_page
g_info: true
permalink: /graduate/research-areas/
nav_parent: Graduate
nav_weight: 2
---

{% assign sorted_people = site.departmentpeople | sort: 'lastname' %}

<h1 class="mb-3">Research areas</h1>

 The Mathematics Department at the University of Virginia offers graduate students the opportunity to do research in a wide range of specialties. To help students with the daunting task of planning their multi-year program, in this guide we describe standard routes through the main research areas that students can currently pursue. We expect most students to follow one of these paths.

 For convenience, we have grouped these within Programs in Algebra, Analysis, Topology, and the History of Mathematics. However, it is to be emphasized that there is much interaction between these, and a course of study might easily fall between areas. Furthermore, research areas undergo constant change due to changing faculty and student interests, and to new faculty joining the Department. Finally, there are a number of possible courses of study not listed here that may involve collaboration with faculty from other departments.

---

<h2>1 Graduate Program in Algebra</h2>

**Faculty:**&nbsp;&nbsp;
{% for ppl in sorted_people %}{% if ppl.grad_general_areas contains "algebra" %}<span style="white-space:nowrap">{% if ppl.email != null %}<a href="mailto:{{ ppl.email }}"><span class="fa fa-envelope" aria-hidden="true" style="font-size:0.8em"></span></a> {% endif %}<a href="{% if ppl.personal_page != null %}{{ ppl.personal_page }}{% else %}{{ site.url }}/people/{{ppl.UVA_id}}{% endif %}">{{ ppl.name | slice: 0 }}. {{ ppl.lastname }}</a></span>; {% endif %}{% endfor %}

Graduate research in algebra is organized into the following areas:
- Linear and Arithmetic Groups and Associated Structures
- Representation Theory
- Commutative Algebra
- Algebraic Geometry
- Algebraic Combinatorics
- Number Theory



<h3>1.1 Core Courses and Requirements in Algebra</h3>

 The following is the list of basic, graduate courses in algebra prerequisite for students intending to pursue studies in algebra:

#### First Year

- _First Semester:_ MATH 7751 Algebra I
- _Second Semester:_ MATH 7752 Algebra II


#### Second Year

- _First Semester:_ MATH 7753 Algebra III (algebras over a field, Artin-Wedderburn theory and the Jacobson radical, applications to representation theory) and MATH 9950 Algebra Seminar.
- _Second Semester:_ MATH 7754 Algebra IV (topics in algebra) and MATH 950 Algebra Seminar

Students also take one additional algebra course in one of the two semesters.

Besides taking the sequence MATH 7751, 7752, 7753, 7754 in their first two years, students with interests in algebra are required - within the first two years - to take at least one additional course in the specialized area of algebra which they expect to follow. The additional course(s) may be an independent reading course taken under the supervision of a faculty member.

#### General exam

The General Exam in Algebra is based on the material of MATH 7751, 7752.

#### Research Seminar

Algebra students are also required to take and to participate actively in MATH 9950 (Algebra Seminar) every semester after the first year. In the <em>first semester of the second year</em>, students contemplating working in algebra should contact a faculty member regarding a topic for a literature survey and, during the <em>second semester</em>, give a short expository talk in the Algebra Seminar.

#### Second-Year Proficiency Exam

In the second year, students take the Second-Year Proficiency Exam, which, in algebra, consists of a conversation with a panel of faculty members on the material of two or three second-year algebra courses taken by the student, and on the bibliographical research done by the student and presented in MATH 9950.



<h3>1.2 Linear and Arithmetic Groups and Associated Structures</h3>

**Faculty:**&nbsp;&nbsp;
{% for ppl in sorted_people %}{% if ppl.grad_special_areas contains "groups" %}<span style="white-space:nowrap">{% if ppl.email != null %}<a href="mailto:{{ ppl.email }}"><span class="fa fa-envelope" aria-hidden="true" style="font-size:0.8em"></span></a> {% endif %}<a href="{% if ppl.personal_page != null %}{{ ppl.personal_page }}{% else %}{{ site.url }}/people/{{ppl.UVA_id}}{% endif %}">{{ ppl.name | slice: 0 }}. {{ ppl.lastname }}</a></span>; {% endif %}{% endfor %}

 Research in this area focuses on structural, combinatorial and homological properties of linear groups over general rings with a special emphasis on arithmetic rings (i.e., the rings of <em>S</em>-integers in global fields). Topics include the normal subgroup structure of the groups of rational points of algebraic groups and of their important subgroups, finiteness properties of arithmetic groups in positive characteristic, the rigidity of representations of finitely generated groups and building theory, in particular, group actions on spherical, affine, and twin buildings. The work in this area requires methods of the theory of algebraic groups, algebraic number theory, homological algebra, and combinatorial geometry/topology.

#### Recommended Advanced Courses

MATH 7600 Homological Algebra, MATH 8851 Group Theory, MATH 8600 Commutative Algebra, MATH 8620 Algebraic Geometry, and special topics courses (or reading courses) in algebraic groups, arithmetic groups, geometric group theory, algebraic number theory, and building theory.


<h3>1.3 Representation Theory</h3>

**Faculty:**&nbsp;&nbsp;
{% for ppl in sorted_people %}{% if ppl.grad_special_areas contains "reptheory" %}<span style="white-space:nowrap">{% if ppl.email != null %}<a href="mailto:{{ ppl.email }}"><span class="fa fa-envelope" aria-hidden="true" style="font-size:0.8em"></span></a> {% endif %}<a href="{% if ppl.personal_page != null %}{{ ppl.personal_page }}{% else %}{{ site.url }}/people/{{ppl.UVA_id}}{% endif %}">{{ ppl.name | slice: 0 }}. {{ ppl.lastname }}</a></span>; {% endif %}{% endfor %}

 Representation theory deals with representations of algebraic and associated finite groups, associative and Lie algebras, and connections with algebraic geometry and mathematical physics. Topics include representations of reductive algebraic groups in positive characteristic with applications to finite groups of Lie type, quantum groups and Hecke algebras, quasi-hereditary algebras and vertex algebras. This work used methods from the theory of algebraic groups and algebraic geometry, Lie algebras, and homological algebra. Moonshine represents the interplay between the number theory of automorphic forms and the representation theory of finite groups.

#### Recommended Advanced Courses

MATH 7600 Homological Algebra, MATH 8851 Group Theory, MATH 8852 Representation Theory, MATH 8620 Algebraic Geometry, MATH 8700 Lie Groups, MATH 8710 Lie Algebras, and special topics courses (or reading courses) in algebraic groups, Kac-Moody algebras, symmetric groups and their representations, Hecke algebras and quantum groups.



<h3>1.4 Commutative Algebra</h3>

**Faculty:**&nbsp;&nbsp;
{% for ppl in sorted_people %}{% if ppl.grad_special_areas contains "commutative" %}<span style="white-space:nowrap">{% if ppl.email != null %}<a href="mailto:{{ ppl.email }}"><span class="fa fa-envelope" aria-hidden="true" style="font-size:0.8em"></span></a> {% endif %}<a href="{% if ppl.personal_page != null %}{{ ppl.personal_page }}{% else %}{{ site.url }}/people/{{ppl.UVA_id}}{% endif %}">{{ ppl.name | slice: 0 }}. {{ ppl.lastname }}</a></span>; {% endif %}{% endfor %}

 Commutative algebra studies the space of solutions of polynomial and power series equations in many variables, often by creating a &quot;generic&quot; solution space, and investigating the properties of this space, and its specializations and deformations.

 In the early 20th century, commutative algebra was born out of three classical fields: algebraic number theory, algebraic geometry, and invariant theory. Today it retains connections to all of these areas, as well as many other areas such as combinatorics, homological algebra, representation theory, computational algebra, singularity theory, and algebraic statistics.

 One of the most important techniques in modern commutative algebra is that of reduction to characteristic <em>p</em>, and the study and classification of singularities through invariants coming from this reduction.


#### Recommended Advanced Courses

MATH 7600, Homological Algebra; MATH 8600, Commutative Algebra; and MATH 8620, Algebraic Geometry.

<h3>1.5 Algebraic Geometry</h3>

**Faculty:**&nbsp;&nbsp;
{% for ppl in sorted_people %}{% if ppl.grad_special_areas contains "algeom" %}<span style="white-space:nowrap">{% if ppl.email != null %}<a href="mailto:{{ ppl.email }}"><span class="fa fa-envelope" aria-hidden="true" style="font-size:0.8em"></span></a> {% endif %}<a href="{% if ppl.personal_page != null %}{{ ppl.personal_page }}{% else %}{{ site.url }}/people/{{ppl.UVA_id}}{% endif %}">{{ ppl.name | slice: 0 }}. {{ ppl.lastname }}</a></span>; {% endif %}{% endfor %}


The <a href="{{site.url}}/seminars/galois/">Galois-Grothendieck seminar</a> is a learning seminar for graduate students, postdocs and faculty that focuses on topics from algebraic and arithmetic geometry and number theory. It is open to graduate students of all years independent of the chosen area of research.

<h3>1.6 Algebraic Combinatorics</h3>

**Faculty:**&nbsp;&nbsp;
{% for ppl in sorted_people %}{% if ppl.grad_special_areas contains "algcomb" %}<span style="white-space:nowrap">{% if ppl.email != null %}<a href="mailto:{{ ppl.email }}"><span class="fa fa-envelope" aria-hidden="true" style="font-size:0.8em"></span></a> {% endif %}<a href="{% if ppl.personal_page != null %}{{ ppl.personal_page }}{% else %}{{ site.url }}/people/{{ppl.UVA_id}}{% endif %}">{{ ppl.name | slice: 0 }}. {{ ppl.lastname }}</a></span>; {% endif %}{% endfor %}


<h3>1.7 Number Theory</h3>

**Faculty:**&nbsp;&nbsp;
{% for ppl in sorted_people %}{% if ppl.grad_special_areas contains "numth" %}<span style="white-space:nowrap">{% if ppl.email != null %}<a href="mailto:{{ ppl.email }}"><span class="fa fa-envelope" aria-hidden="true" style="font-size:0.8em"></span></a> {% endif %}<a href="{% if ppl.personal_page != null %}{{ ppl.personal_page }}{% else %}{{ site.url }}/people/{{ppl.UVA_id}}{% endif %}">{{ ppl.name | slice: 0 }}. {{ ppl.lastname }}</a></span>; {% endif %}{% endfor %}


---

<h2>2 Graduate Program in Analysis</h2>


**Faculty:**&nbsp;&nbsp;
{% for ppl in sorted_people %}{% if ppl.grad_general_areas contains "analysis" %}<span style="white-space:nowrap">{% if ppl.email != null %}<a href="mailto:{{ ppl.email }}"><span class="fa fa-envelope" aria-hidden="true" style="font-size:0.8em"></span></a> {% endif %}<a href="{% if ppl.personal_page != null %}{{ ppl.personal_page }}{% else %}{{ site.url }}/people/{{ppl.UVA_id}}{% endif %}">{{ ppl.name | slice: 0 }}. {{ ppl.lastname }}</a></span>; {% endif %}{% endfor %}

Graduate research in analysis is organized into the following areas:
- Differential Equations and Related Applied Mathematics
- Mathematical Physics
- Operator Theory, Operator Algebras, and Function Theory
- Harmonic Analysis
- Probability and Related Applied Mathematics



<h3>2.1 Core Courses and Requirements in Analysis</h3>

 Students intending to do research in some area of analysis must take the following courses:

#### First Year



- MATH 7310 Real Analysis and Linear Spaces I, MATH 7340 Complex Analysis I


#### Second Year



- _First Semester:_ MATH 7410 Functional Analysis I


 Additional courses and requirements depend on the specific research area selected by a student, as specified below.

#### General exam

The General Exam in Analysis has two parts: the first part based on material from MATH 7310, and the second part based on material from one of MATH 7340, MATH 7250, and MATH 7360. For students planning to work in analysis, the second part of the general exam should fit with the area they are pursuing.

#### Research Seminars

Students in analysis in the second year and beyond are expected to participate in one of the analysis research seminars. These seminars are an important component of the graduate program, and are student-oriented. They aim to expand upon material covered in the various courses and to prepare students for independent reading of research papers.

 In the <em>first semester of the second year</em>, students contemplating working in an area of analysis should contact a faculty member regarding a topic for a literature survey, and, during the <em>second semester</em>, give a short talk in the appropriate seminar.

#### Second-Year Proficiency Exam

Also in the second year, students take the Second-Year Proficiency Exam, which, in analysis, consists of a conversation with a panel of faculty members on the material from two or three second-year analysis courses, and and on the bibliographical research done by the student for their seminar presentation.

<h3>2.2 Differential Equations and Related Applied Mathematics</h3>

**Faculty:**&nbsp;&nbsp;
{% for ppl in sorted_people %}{% if ppl.grad_special_areas contains "diffeq" %}<span style="white-space:nowrap">{% if ppl.email != null %}<a href="mailto:{{ ppl.email }}"><span class="fa fa-envelope" aria-hidden="true" style="font-size:0.8em"></span></a> {% endif %}<a href="{% if ppl.personal_page != null %}{{ ppl.personal_page }}{% else %}{{ site.url }}/people/{{ppl.UVA_id}}{% endif %}">{{ ppl.name | slice: 0 }}. {{ ppl.lastname }}</a></span>; {% endif %}{% endfor %}

 This area focuses on the qualitative study of solutions of differential equations: ordinary differential equations (ODE&#39;s) as well as partial differential equations (PDE&#39;s), both linear and nonlinear. Particular emphasis is placed on equations arising in mathematical physics and related areas of applied mathematics. Topics of study include fluid dynamics, linear and nonlinear elasticity and wave propagation, harmonic analysis, dynamical systems, and control theory. The mathematical methods used draw from real and complex analysis, functional analysis, harmonic analysis, ordinary and partial differential equations, basic differential geometry, and probability.

#### Area Coursework

Besides the three common core analysis courses, students should also take MATH 7250 (Ordinary Differential Equations I) as soon as possible. In the second year, students should take MATH 8250 Partial Differential Equations I, and, if possible, MATH 7320 (Real Analysis II) and MATH 7420 (Functional Analysis II). They should also begin attending MATH 9250 (Differential Equations Seminar). Students should try to take the General Exam in analysis on MATH 7310 and MATH 7250; however, the combination of MATH 7310/7340 is also acceptable.

#### Recommended Advanced Courses

MATH 726 (Ordinary Differential Equations II) and MATH 826 (Partial Differential Equations II), possibly in reading course format. Also MATH 7360 (Probability), MATH 8310 (Operator Theory I), MATH 8360 (Stochastic Differential Equations), MATH 7450 (Mathematical Physics), and MATH 8720 (Differential Geometry).







<h3>2.3 Mathematical Physics</h3>


**Faculty:**&nbsp;&nbsp;
{% for ppl in sorted_people %}{% if ppl.grad_special_areas contains "math_physics" %}<span style="white-space:nowrap">{% if ppl.email != null %}<a href="mailto:{{ ppl.email }}"><span class="fa fa-envelope" aria-hidden="true" style="font-size:0.8em"></span></a> {% endif %}<a href="{% if ppl.personal_page != null %}{{ ppl.personal_page }}{% else %}{{ site.url }}/people/{{ppl.UVA_id}}{% endif %}">{{ ppl.name | slice: 0 }}. {{ ppl.lastname }}</a></span>; {% endif %}{% endfor %}

 Our research in mathematical physics is concerned with the spectral and scattering theory for Schroedinger operators in quantum mechanics, equilibrium and non-equilibrium statistical mechanics, and topics in classical mechanics. The mathematical methods needed include: real analysis--measure theory and integration; functional analysis--for example, operators in Hilbert spaces; Fourier analysis; partial differential equations; and some basic probability theory. 
 Real variable methods for inverse scattering theory as a topic.

#### Area Coursework

Besides the three common core analysis courses, students should also take as soon as possible MATH 7250 (Ordinary Differential Equations I). In the second year, students should take, if possible, MATH 7320 (Real Analysis II), MATH 7420 (Functional Analysis II), MATH 7450 (Mathematical Physics), and participate in MATH 9450 (Mathematical Physics Seminar). Math physics students should take their General Exam in analysis on MATH 7310 and MATH 7340.

#### Recommended Advanced Courses

MATH 8250 (Partial Differential Equations), MATH 7360 (Probability), MATH 8450 (Topics in Mathematical Physics) as appropriate to the student&#39;s thesis work.







<h3>2.4 Operator Theory, Function Theory, and Operator Algebras</h3>

**Faculty:**&nbsp;&nbsp;
{% for ppl in sorted_people %}{% if ppl.grad_special_areas contains "operators" %}<span style="white-space:nowrap">{% if ppl.email != null %}<a href="mailto:{{ ppl.email }}"><span class="fa fa-envelope" aria-hidden="true" style="font-size:0.8em"></span></a> {% endif %}<a href="{% if ppl.personal_page != null %}{{ ppl.personal_page }}{% else %}{{ site.url }}/people/{{ppl.UVA_id}}{% endif %}">{{ ppl.name | slice: 0 }}. {{ ppl.lastname }}</a></span>; {% endif %}{% endfor %}

 Our research on Hilbert space operators draws broadly from functional analysis and has two main (interrelated) strands. One is rooted in complex function theory and concerns composition, Toeplitz, and other operators on spaces of analytic functions. The other studies algebraic structures of operators: von Neumann algebras, C*-algebras, operator spaces, and noncommutative function spaces.

#### Area Coursework

Besides the three common core analysis courses, students should take MATH 8310 (Operator Theory) or MATH 8300 (Function Theory) by the end of their second year. Also in the second year, students should take, if available, one or both of MATH 7320 (Real Analysis II) and MATH 7350 (Complex Analysis II), as well as MATH 7420 (Functional Analysis II). Beginning in the second year, students should participate in MATH 9310 (Operator Theory Seminar). Students should take their Ph.D. General Exam in analysis in MATH 7310 and MATH 7340.

#### Recommended Advanced Courses

MATH 7250 (Ordinary Differential Equations), MATH 7360 (Probability Theory), MATH 7450 (Mathematical Physics), MATH 8250 (Ordinary Differential Equations), MATH 8320 (Operator Theory II), MATH 8400 (Harmonic Analysis).


<h3>2.5 Harmonic Analysis</h3>

**Faculty:**&nbsp;&nbsp;
{% for ppl in sorted_people %}{% if ppl.grad_special_areas contains "harmonic" %}<span style="white-space:nowrap">{% if ppl.email != null %}<a href="mailto:{{ ppl.email }}"><span class="fa fa-envelope" aria-hidden="true" style="font-size:0.8em"></span></a> {% endif %}<a href="{% if ppl.personal_page != null %}{{ ppl.personal_page }}{% else %}{{ site.url }}/people/{{ppl.UVA_id}}{% endif %}">{{ ppl.name | slice: 0 }}. {{ ppl.lastname }}</a></span>; {% endif %}{% endfor %}

Fourier analysis and boundedness of multilinear operators, focusing on time-frequency analysis and its recent development, motivated by studies of pointwise convergence of Fourier series and boundedness of the Bilinear Hilbert transform and variants. 

#### Area Coursework

Real Analysis, Complex Analysis, Functional Analysis, Probability Theory, and Topics In Harmonic Analysis.


<h3>2.6 Probability and Related Applied Mathematics</h3>

**Faculty:**&nbsp;&nbsp;
{% for ppl in sorted_people %}{% if ppl.grad_special_areas contains "probability" %}<span style="white-space:nowrap">{% if ppl.email != null %}<a href="mailto:{{ ppl.email }}"><span class="fa fa-envelope" aria-hidden="true" style="font-size:0.8em"></span></a> {% endif %}<a href="{% if ppl.personal_page != null %}{{ ppl.personal_page }}{% else %}{{ site.url }}/people/{{ppl.UVA_id}}{% endif %}">{{ ppl.name | slice: 0 }}. {{ ppl.lastname }}</a></span>; {% endif %}{% endfor %}

 Probability is the mathematical theory of random events and random variables. Areas of particular interest to faculty include central limit theorems, Malliavin calculus, stochastic differential equations, Markov and L&egrave;vy processes, stochastic networks, measure-valued processes, roots of random polynomials, and applications to operations research and mathematical biology. 
 

#### Area Coursework

Besides the three common core analysis courses, students should take MATH 7360 (Probability Theory I) and MATH 737 (Probability Theory II) as soon as possible. These are typically offered in the Spring and Fall respectively, so that students can begin in the Spring of their first year after taking 7310. In the second year, students should take MATH 8360 (Stochastic Calculus and Differential Equations). Students should also participate in MATH 9360 (Probability Seminar). Students should take their Ph.D. General Exam in analysis in MATH 7310 and MATH 7360.

#### Recommended Advanced Courses

MATH 8370 (Topics in Probability), MATH 7320 (Real Analysis II), MATH 7420 (Functional Analysis II), MATH 8250 (Partial Differential Equations), MATH 8310 (Operator Theory), MATH 8720 (Differential Geometry) as appropriate to the student&#39;s thesis work.

---

<h2>3&nbsp;Graduate Program in Geometry and Topology</h2>

**Faculty:**&nbsp;&nbsp;
{% for ppl in sorted_people %}{% if ppl.grad_general_areas contains "geometry" %}<span style="white-space:nowrap">{% if ppl.email != null %}<a href="mailto:{{ ppl.email }}"><span class="fa fa-envelope" aria-hidden="true" style="font-size:0.8em"></span></a> {% endif %}<a href="{% if ppl.personal_page != null %}{{ ppl.personal_page }}{% else %}{{ site.url }}/people/{{ppl.UVA_id}}{% endif %}">{{ ppl.name | slice: 0 }}. {{ ppl.lastname }}</a></span>; {% endif %}{% endfor %}

Graduate research in topology is organized into the following areas:
- Algebraic Topology
- Low-Dimensional Topology and Geometry

We must emphasize that these areas have a lot in common, so the subdivision into &quot;algebraic&quot; and &quot;geometric&quot; is not always precise.




<h3>3.1 Core Courses and Requirements in Topology</h3>

 The following is the list of basic graduate courses prerequisite for students intending to pursue research in topology:

#### First Year



- _First Semester:_ MATH 7820 Differential Topology (recommended).
- _Second Semester:_ MATH 7800 Algebraic Topology I (fundamental group and covering spaces, singular and simplicial homology).


#### Second Year



- _First Semester:_ MATH 7810 Algebraic Topology II (cohomology, Poincar&eacute; duality) and MATH 9800 Topology Seminar.
- _Second Semester:_ MATH 7830 Fiber Bundles (vector bundles, characteristic classes, elements of K-theory) and MATH 9800 Topology Seminar. In addition, during the second year students should take at least one additional topology course.


 The course MATH 7830 will be offered in the Spring semester each year. Besides taking the sequence MATH 7820, 7800, 7810, 7830, students with interests in topology are required--within the first two years--to take at least one additional course in the specialized area or track of topology (see below) which they expect to follow. These additional courses may be independent reading courses taken under the supervision of a faculty member.

#### General exam

The General Exam in Topology is based on the material of MATH 7820, 7800.

#### Research Seminar

Topology/geometry students are expected to take and to participate actively in the topology and/or geometry seminars every semester after the first year. There are normally two seminars weekly: geometric topology on Tuesdays, algebraic topology on Thursdays. Participants should attend either the Tuesday seminar or the Thursday seminar (or both), but in either case will register for MATH 9820 Geometry and Topology Seminar.

#### Second-Year Proficiency Exam

In the second year, students take the Second-Year Proficiency Exam, which, in topology, consists of a conversation with a panel of faculty members on the material of two or three topology courses taken by the student during the second year, and on the bibliographical research done by the student and presented in MATH 9800.







<h3>3.2 Algebraic Topology</h3>


**Faculty:**&nbsp;&nbsp;
{% for ppl in sorted_people %}{% if ppl.grad_special_areas contains "alg_top" %}<span style="white-space:nowrap">{% if ppl.email != null %}<a href="mailto:{{ ppl.email }}"><span class="fa fa-envelope" aria-hidden="true" style="font-size:0.8em"></span></a> {% endif %}<a href="{% if ppl.personal_page != null %}{{ ppl.personal_page }}{% else %}{{ site.url }}/people/{{ppl.UVA_id}}{% endif %}">{{ ppl.name | slice: 0 }}. {{ ppl.lastname }}</a></span>; {% endif %}{% endfor %}

 The subject of algebraic topology is the interplay between topology and algebra. One associates algebraic objects, e.g., groups and rings, with topological spaces in a &#39;natural&#39; way, and investigates how the algebraic invariants reflect the topological structure of the spaces. Research in this area requires a good understanding of both topology and algebra. Areas of particular interest to faculty include homotopical algebra and homotopy as organized by the calculus of functors, group cohomology and its connections to representation theory and algebraic <em>K</em>-theory, and the study of complex oriented cohomology theories. There are deep connections with many parts of algebra, including algebraic geometry and number theory, and mathematical physics.

#### Recommended Advanced Courses

MATH 7840 Homotopy Theory, MATH 8800 Generalized Cohomology, MATH 7600 Homological Algebra, MATH 8700 Lie Groups, MATH 8650 Algebraic <em>K</em>-Theory, MATH 8830 Cobordism and K-Theory, and special topics (or reading courses) in calculus of functors and homotopical algebra.







<h3>3.3&nbsp;Low-Dimensional Topology and Geometry</h3>


**Faculty:**&nbsp;&nbsp;
{% for ppl in sorted_people %}{% if ppl.grad_special_areas contains "geom_top" %}<span style="white-space:nowrap">{% if ppl.email != null %}<a href="mailto:{{ ppl.email }}"><span class="fa fa-envelope" aria-hidden="true" style="font-size:0.8em"></span></a> {% endif %}<a href="{% if ppl.personal_page != null %}{{ ppl.personal_page }}{% else %}{{ site.url }}/people/{{ppl.UVA_id}}{% endif %}">{{ ppl.name | slice: 0 }}. {{ ppl.lastname }}</a></span>; {% endif %}{% endfor %}

 The central subject of geometric topology is the theory of manifolds, their classification, and study of their geometric properties. Research areas represented by the faculty include knot theory, quantum invariants of three-dimensional manifolds, geometric and differential four-dimensional topology, gauge theory, groups acting on manifolds, hyperbolic geometry, and moduli spaces of geometric structures.&nbsp; This area has deep connections with algebraic topology, representation theory, geometric analysis and mathematical physics.

 Note that the topic of Math 8750 Topology of Manifolds varies with each offering, and will not necessarily correspond to the catalog description. Students considering this course should contact the instructor or the director of graduate studies for a course description.


#### Recommended Advanced Courses

MATH 8750 Topology of manifolds, MATH 8830 Cobordism and <em>K</em>-Theory, MATH 8720 Differential Geometry, MATH 7840 Homotopy Theory, and special topics courses (or reading courses) in characteristic classes, knot theory, 4-dimensional topology.


---

<h2>4 Graduate Program in the History of Mathematics</h2>


**Faculty:**&nbsp;&nbsp;
{% for ppl in sorted_people %}{% if ppl.grad_general_areas contains "history" %}<span style="white-space:nowrap">{% if ppl.email != null %}<a href="mailto:{{ ppl.email }}"><span class="fa fa-envelope" aria-hidden="true" style="font-size:0.8em"></span></a> {% endif %}<a href="{% if ppl.personal_page != null %}{{ ppl.personal_page }}{% else %}{{ site.url }}/people/{{ppl.UVA_id}}{% endif %}">{{ ppl.name | slice: 0 }}. {{ ppl.lastname }}</a></span>; {% endif %}{% endfor %}

 The graduate program in the history of mathematics includes a component in the history of science taken within the Department of History. Students in the program must satisfy all of the requirements for the Ph.D. in Mathematics. In particular, they must complete the coursework in mathematics and perform satisfactorily on General Examinations in two areas before they are permitted to proceed toward the doctorate. Strong reading competency in either French or German is required for admission into the program, with strong reading competency required in the other language by the time dissertation research begins. Depending on a particular student&#39;s interests, other languages may also be required.

 <strong>Program Coursework</strong>
The following is typical for a student in the graduate program in the history of mathematics:

#### First Year



- _First Semester:_ MATH 7310 (Real Analysis), MATH 7510 (Algebra I), MATH 5770 (General Topology), or one additional mathematics course (to be determined depending on the student&#39;s future historical interests).
- _Second Semester:_ MATH 7320 (Real Analysis II), MATH 7520 (Algebra II), one additional mathematics course (again to be determined depending on the student&#39;s future historical interests). General exams are taken at the end of the summer after the first year.


#### Second Year





- _First Semester:_ MATH 7753 (Algebra III), HIEU 3321 (The Scientific Revolution) (taken as MATH 9999), MATH 7340 (Complex Analysis), or one additional mathematics course depending on specific interests and needs, MATH 7000, and MATH 9010.
- _Second Semester:_ MATH 5010 (The History of the Calculus) or MATH 5030 (The History of Mathematics) (depending on the year), HIUS 3401 (The Development of American Science) (taken as MATH 9999), MATH 7800 (Algebraic Topology I), or one additional course depending on specific needs and interests. The summer after the second year involves directed readings geared toward the isolation of an eventual dissertation topic.


#### Third Year and Beyond

Additional mathematics courses to complete the number of hours required for the degree (chosen in consultation with the adviser), and any additional courses as needed (in, for example, language(s), history, or philosophy).

#### Research Seminar

Students are expected to participate actively in MATH 9010 History of Mathematics Seminar in all semesters.

#### Dissertation Proposal

For students in this program, the proposal defense replaces the Second-Year Proficiency Exam. It generally takes place before the end of the third year. Successful defense of the proposal represents &quot;permission to proceed&quot; to the dissertation phase of the program. The proposal is a written document (generally thirty to forty pages in length, exclusive of bibliography) that is presented in a public forum. It


- details and justifies the historical questions the student proposes to explore in the dissertation;
- provides a detailed sketch of what the dissertation will cover, how it will be organized, and why;
- situates the proposed work within the broader literature of the history of science and mathematics; and
- provides a detailed (first approximation) of the dissertation&#39;s bibliography.
