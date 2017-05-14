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

Mathematical $$\mathrm{\LaTeX}$$ formulas are supported on this webpage via [MathJax](https://www.mathjax.org/), a powerful external Javascript library.
We refer to MathJax's documentation for full details.
Here are just some things to note:

- Math formulas can be included in any markdown field by surrounding them by double dollars (*not* single dollars as in the usual $$\mathrm{\LaTeX}$$). For example, code `$$\int_0^T t\,dt=\frac{T^2}2$$` produces this: $$\int_0^T t\,dt=\frac{T^2}2$$.
- Display formulas are simply put in a separate line (with empty lines above and below), and are also surrounded by double dollar signs. Example:

$$\int_0^T W_t\,dW_t=\frac12\bigl(W_T^2-T^2\bigr).$$

- Complicated $$\mathrm{\LaTeX}$$ macros or whole mathematical texts pasted onto a page might not render correctly.
