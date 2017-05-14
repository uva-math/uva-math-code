---
title: Virginia Mathematics Lectures
layout: static_page_no_right_menu
permalink: /ims/lectures/
nav_id: 'Virginia Mathematics Lectures (2014-)'
nav_weight: 2
# nav_nesting: true
nav_parent: IMS
---

<h1 class="mb-5">Virginia Mathematics Lectures</h1>


In 2014, the IMS established the Distinguished Lecture Series "Virginia Mathematics Lectures." The inaugural speaker was Professor Alex Lubotzky from the Hebrew University of Jerusalem. Each semester thereafter brought us another speaker in the series, including Vaughan Jones (Vanderbilt), Ian Agol (UC Berkeley), and – most recently – Benedict H. Gross (Harvard).

These lecture series were enthusiastically met by the audience which included undergraduate and graduate students, faculty members and guests from other departments and institutions. Given the success of the lectures, the IMS will continue to organize two such series every year.


### Past lectures

- Benedict H. Gross (Harvard University), Spring 2017
- James Arthur (University of Toronto), Fall 2016
- Karen Smith (University of Michigan), Spring 2016
- Ian Agol (University of California Berkeley), Fall 2015
- Vaughan Jones (Vanderbilt University), Spring 2015
- Alex Lubotzky (Hebrew University of Jerusalem), Fall 2014

<br>

<div class="row my-col-12-zebra">
{% for post in site.posts %}
{% if post.categories contains "virginia-mathematics-lectures" %}
<div class="col-12 my-bordered-news-snippets">
<h3 class="mb-2 mt-3"><a href="{{site.url }}{{ post.url }}" style="color:inherit;">{{ post.title }}</a></h3> {% if post.event-date != null %}
<h6>{{ post.event-date |  date: "%A, %B %-d, %Y" }}</h6>{% endif %} {% if post.image != null %} {% if post.image-address != null %}<a href="{{ post.image-address | replace: '__SITE_URL__', site.url }}">{% else %}<a href="{{site.url }}{{ post.url }}">{% endif %}<img src="{{ post.image | replace: '__SITE_URL__', site.url }}" alt="{{ post.image-alt }}" title="{{ post.image-alt }}" style="max-width:600px;height:auto;width:auto;" class="mb-3 mt-2"></a>
{% endif %} {{ post.excerpt | markdownify }}
<p><a class="btn btn-secondary h5" href="{{site.url }}{{ post.url }}" role="button">{% if post.more-text == null %}View details{% else %}{{ post.more-text }}{% endif %} &raquo;</a></p>
</div>
<!--/span-->
{% endif %}
{% endfor %}
</div>



## <a name="smith"></a>Karen Smith (University of Michigan) February 29th - March 2nd, 2016

### Algebra, Geometry and Analysis over Finite Fields

#### Lecture 1

*Abstract:* In this lecture, we review how Noether's introduction of the concept of an abstract ring changed the course of mathematics in the twentieth century by enabling us to apply the methods of  "reduction modulo p" to solve problems in algebraic geometry. Specifically, I'll discuss how understanding solutions to polynomials over finite fields can help understand the geometry of geometric objects (called varieties) defined by real or complex polynomials. Miraculously, rings of characteristic p have some very special properties that can be powerful tools in analyzing them, often replacing tools like integration for real manifolds.

#### Lecture 2

*Abstract:* In the second lecture, we review Hironaka's famous theorem on the resolution of singularities of a complex algebraic variety. We show this theorem can help us understand and measure the singularities of complex varieties. Amazingly, it turns out that the only algebraic characterization of a geometric condition called "rational singularities" involves reduction to characteristic p. Specifically, we will see how algebraic tools such as Frobenius splitting impact  different areas of math, including the minimal model program for complex algebraic varieties and cluster algebras in combinatorics/representation theory.



#### Lecture 3

*Abstract:* In the final lecture, we discuss a numerical invariant of singularities called the analytic index of singularities, which is defined by the convergence of a certain integral. Amazingly, this invariant turns out to have a prime characteristic description as well, as the limit, over all primes p, of another invariant called the F-pure threshold. The study of these F-pure thresholds leads to some very interesting and mysterious fractal like behavior.


<img src="{{site.url}}/img/IMS/Karen_Smith_poster_4_0.jpg" style="max-width:80%" alt="Virginia Mathematics Lectures">

<hr>

## <a name="agol"></a> Ian Agol (Berkeley) October 14th-16th, 2015

### The Virtual Haken Conjecture

*Abstract:* Waldhausen conjectured in 1968 that every aspherical 3-manifold has a finite-sheeted cover which is Haken (contains an embedded essential surface). Thurston conjectured that hyperbolic 3-manifolds have a finite-sheeted cover which fibers over the circle.

#### An overview of 3-Manifold Topology

*Abstract:* The first lecture will be an overview of  3-manifold topology in order to explain the meaning Waldhausen's virtual Haken conjecture and Thurston's virtual fibering conjecture, and how they relate to other problems in 3-manifold theory.


#### Lecture 2: What is Geometric Group Theory?

*Abstract:* The second lecture will give some background on geometric group theory, including the topics of hyperbolic groups and $$CAT(0)$$ cube complexes after Gromov, and explain how the above conjectures may be reduced to a conjecture of Dani Wise in geometric group theory.


#### Lecture 3: Geometric Group Theory and the Virtual Haken Conjecture

*Abstract:*  The third lecture will discuss the proof of Wise's conjecture, that cubulated hyperbolic groups are virtually special. Part of this result is joint work with Daniel Groves and Jason Manning. We will attempt to make these lectures accessible to a general mathematical audience at the level of a colloquium talk.


<img src="{{site.url}}/img/IMS/Agol_poster_5_0.jpg" style="max-width:80%" alt="Virginia Mathematics Lectures">

<hr>

## <a name="jones"></a> Vaughan Jones (Vanderbilt University) April 6th-8th, 2015

#### Lecture 1:  Knots and Groups

*Abstract:* Knots are among the more concrete features in the mathematical landscape. Groups are more pervasive and more abstract. But the two subjects have been intimately connected since the early days of the study of both. After defining knots and groups we will give the first such connection-the "fundamental group" of the knot. This group is known to determine the knot but a construction is not immediate. The braid group is a concrete group with some structural resemblance to knots. We will show how all knots arise from elements of the braid group and how to learn things about the knot from its braid.  In particular a family of “knot polynomials” appears from this study.


#### Lecture 2: Von Neumann Algebra and Physics

*Abstract:*  The states of a quantum system are given by vectors in a Hilbert space with inner product $$\langle \xi,\eta \rangle$$. Observables are self-adjoint operators on that Hilbert space. The fundamental formula connecting the two is that if $$a$$ is an operator/observable and $$\xi$$ is a unit vector/state then $$\langle a\xi,\eta \rangle$$ is a real number giving the average value of repeated measurements of the observable $$a$$ if the system is prepared each time in the state $$\xi$$. Von Neumann introduced the algebras that bear his name in large part to help understand the mathematical structure of quantum theory. His prophetic ideas have been very fruitful in low dimensional quantum field theory and are intimately related to the knot polynomials of the first lecture.


#### Lecture 3: Do all Subfactors arise in Conformal Field Theory?

*Abstract:* A subfactor is a pair of von Neumann algebras with trivial center (factors) one included in the other. A subfactor $$N \subset M$$ has an index $$[M : N]$$ which is a real number defined by von Neumann’s theory. For the most obvious examples of factors $$[M : N]$$ is actually an integer but in fact it can be any number in the set $$\{4\cos^2(\frac\pi n) \colon n = 3, 4, 5, 6, ...\} \cup [4, \infty]$$. Subfactors realising these values can be constructed from algebras of observables as in the second lecture. It is an open and intriguing question whether or not ALL subfactors (of finite index) can be obtained from quantum field theory. An attempt to take a continuum limit from the data of a subfactor has led to a new construction of knots and links from certain groups of homeomorphisms of the unit interval known as the Thompson groups.


<img src="{{site.url}}/img/IMS/Jones_poster_3_0.jpg" style="max-width:80%" alt="Virginia Mathematics Lectures">

<hr>



## <a name="lubotzky"></a> Alex Lubotzky (Hebrew University of Jerusalem) November 18th-20th, 2014


### Expanders: From One-Dimensional to Multi-Dimensional

#### Lecture 1: Expander Graphs and Geometric/Topological Expanders

*Abstract:* Expander graphs have played an important role, in the last four decades, in many areas of computer science. Recently they have already found applications in pure mathematics. We describe some of this history and present in these three talks some recent efforts to build a high-dimensional theory of expanders. We will start with Gromov's geometric and topological expanders.

#### Lecture 2: From Ramanujan Graphs to Ramanujan Complexes

*Abstract:* Ramanujan graphs are optimal expanders. Their explicit construction is based on deep results of Deligne and Drinfeld in the theory of automorphic forms of $$GL(2)$$. The work of Lafforgue for $$GL(d)$$ enables the developments of high-dimensional objects: the Ramanujan complexes. These simplical complexes/hyper graphs enjoy some remarkable properties, being random-like but at the same time very symmetric. We will show how this helps to solve some problems in computer science (e.g., error-correcting codes) and in geometry.

#### Lecture 3: Coboundary Expanders and Property Testing

*Abstract:* Another direction of generalizing expanders from graphs to simplical complexes was proposed independently by Linial-Meshulam (in the context of developing Erodos-type theory of random simplical complexes) and by Gromov (when studying overlapping properties). We explain this notion and show a surprising connection with "property testing" which is a subject of fundamental importance, in theory and practice, in computer science.


<img src="{{site.url}}/img/IMS/Lubotzky8x14_5_0.jpg" style="max-width:80%" alt="Virginia Mathematics Lectures">
