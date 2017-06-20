---
title: Support for mathematical formulas
layout: documentation_page
permalink: /doc/math/
nav_parent: Info
doc_page: true
nav_weight: 107
---

# Support for math formulas

---

Mathematical <script type="math/tex">\mathrm{\LaTeX}</script> formulas are supported on this webpage via [MathJax](https://www.mathjax.org/) and/or [KaTeX](https://khan.github.io/KaTeX/), powerful external Javascript libraries.
We refer to their respective documentations for full details.

## KaTeX

- KaTeX renders math much faster, but it is under an active development and thus can render with errors

- To render with KaTeX, include the math formulas in a `.md` file in surrounding single dollars or `\\(\\)` (for inline math), and double dollars or `\\[\\]` (for display math)

- For example, code `$\int_0^T t\,dt=\frac{T^2}2$` produces this: $\int_0^T t\,dt=\frac{T^2}2$.

- Display formula example: \\[\int_0^T W_t\,dW_t=\frac12\bigl(W_T^2-T^2\bigr).\\]

- To get display math with dollar signs one needs to use double dollars and put this math expression onto a separate line. Otherwise the math will render inline.

## MathJax

- The fallback mechanism is MathJaX, it is used to render the <script type="math/tex">\mathrm{\LaTeX}</script> logos on this page, using the code `<script type="math/tex">\mathrm{\LaTeX}</script>`

- Display math can be done with MathJaX as `<script type="math/tex; mode=display">\mathrm{\LaTeX}</script>` as below: <script type="math/tex; mode=display">\mathrm{\LaTeX}</script>

- Complicated <script type="math/tex">\mathrm{\LaTeX}</script> macros or whole mathematical texts pasted onto a page might not render correctly with either of the engines.
