# UVA Math TT Roster Verification Worksheet

Purpose: verify the tenure-track/faculty roster used by the UVA arXiv tracker. This file is a review worksheet only; it does **not** edit `_departmentpeople/faculty/`.

Base generated data: `scripts/uva_arxiv/cache/active_people_by_year.json`, generated 2026-06-02T13:25:50Z, initial arXiv start date 2021-08-01.

## Counting distinction

- **arXiv date matching** should use whether a person was plausibly affiliated with UVA on the paper date. Leaves/retirements need exact-ish effective dates, but source affiliation evidence can still matter.
- **Active TT headcount** should follow the department-report convention. For Fall 2026 this excludes John Imbrie and Ken Ono.
- The website people files currently still list both `ji2k` and `ko5wk` under `_departmentpeople/faculty/`; that is why the git-only current-open roster gives 26.

## Known corrections / decisions to verify

| UVA id | Person | Proposed tracker interpretation | Effective date | Evidence / note | Verified? |
|---|---|---|---|---|---|
| `ko5wk` | Ken Ono | Exclude from active TT headcount; keep as faculty/on-leave status for date-sensitive arXiv matching until manually resolved | 2026-01-01 | LP: on extended leave since Jan 2026; department report footnote: extended leave, return uncertain | [x] |
| `ji2k` | John Imbrie | Retired/departed from active TT roster; keep pre-retirement papers as faculty matches | exact date TBD, probably spring/summer 2026 | Department report: retirement this spring / 2025-26 departure | [x] |

## Snapshot counts

| Snapshot | Date used | Git-only active faculty | Adjusted active TT count | Report target / note |
|---|---:|---:|---:|---|
| Spring 2020 report baseline | 2020-05-01 | 29 | 29 | 29 |
| Start AY 2021-22 | 2021-08-01 | 29 | 29 |  |
| Start AY 2022-23 | 2022-08-01 | 27 | 27 |  |
| Start AY 2023-24 | 2023-08-01 | 27 | 27 |  |
| Start AY 2024-25 | 2024-08-01 | 26 | 26 |  |
| Start AY 2025-26 | 2025-08-01 | 26 | 26 |  |
| Ono leave begins | 2026-01-01 | 26 | 25 |  |
| As-of 2026-06-02 | 2026-06-02 | 26 | 24 |  |
| Fall 2026 report endpoint | 2026-08-01 | 26 | 24 | 24 |

## Reconciliation with department-report transition table

| Report row | Departures | Arrivals | Tracker/gitrepo check |
|---|---|---|---|
| Spring 2020 baseline | — | — | git snapshot on 2020-05-01 gives 29 |
| 2020-21 | Herbst | — | `iwh` active in git through 2021-08-20 |
| 2021-22 | Huneke | — | `clh4xd` active in git through 2022-07-31 |
| 2022-23 | Grujic, K. Parshall | — | `zg7c` and `khp3k` active in git through 2023-08-15 |
| 2023-24 | Kuhn | Quigley | `njk4x` active through 2024-07-31; `mbp6pj` starts 2023-08-15 |
| 2024-25 | — | Farhat | `af7py` faculty interval starts 2024-07-31 |
| 2025-26 | Imbrie, Ono* | — | website git has both still open; tracker needs manual active-headcount/status correction |
| Fall 2026 total | — | — | git-only 26; adjusted 24 after excluding Ono from 2026-01-01 and Imbrie from 2026-06-01 |

`*` Ono: extended leave, return uncertain; LP says leave began Jan 2026.

## Snapshot detail: Spring 2020 report baseline (2020-05-01)

Git-only count: 29. Adjusted active-TT count: 29.

| Count? | Person | UVA id | Position in git interval | Interval | Note |
|---|---|---|---|---|---|
| yes | Abdelmalek Abdesselam | `aa4cr` | Associate Professor | 2017-05-10--open |  |
| yes | Peter Abramenko | `pa8e` | Professor | 2017-06-19--open |  |
| yes | Julie Bergner | `jeb2md` | Professor | 2019-07-27--2023-08-22 |  |
| yes | Yen Do | `yqd3p` | Assistant Professor | 2017-06-19--2020-08-20 |  |
| yes | Mikhail Ershov | `mve2x` | Professor | 2018-08-30--open |  |
| yes | Juraj Földes | `jf8dc` | Assistant Professor | 2017-06-19--2022-06-09 |  |
| yes | Evangelia Gazaki | `eg4va` | Assistant Professor | 2019-08-20--2025-08-26 |  |
| yes | Christian Gromoll | `hcg3m` | Associate Professor | 2017-05-06--open |  |
| yes | Zoran Grujic | `zg7c` | Professor | 2018-08-29--2023-08-15 |  |
| yes | Benjamin Hayes | `brh5c` | Assistant Professor | 2017-08-04--2022-06-09 |  |
| yes | Ira Herbst | `iwh` | Professor and Associate Chair | 2019-08-23--2021-08-20 |  |
| yes | Craig Huneke | `clh4xd` | Marvin Rosenblum Professor | 2017-08-04--2022-07-31 |  |
| yes | John Imbrie | `ji2k` | Professor & Chair | 2018-08-29--2021-08-20 |  |
| yes | Thomas Koberda | `tmk5a` | Associate Professor | 2019-07-27--2022-08-08 |  |
| yes | Slava Krushkal | `vk6e` | Professor | 2019-08-23--open |  |
| yes | Nicholas Kuhn | `njk4x` | Professor | 2017-06-19--2024-07-31 |  |
| yes | Sara Maloni | `sm4cw` | Assistant Professor | 2017-06-19--2022-06-09 |  |
| yes | Thomas Mark | `tmark` | Professor | 2019-07-27--2021-08-20 |  |
| yes | Tai Melcher | `tam7b` | Associate Professor | 2017-06-19--open |  |
| yes | Jennifer Morse | `jlm6cj` | Professor | 2017-05-06--open |  |
| yes | Ken Ono | `ko5wk` | Thomas Jefferson Professor of Mathematics | 2019-07-27--2021-08-20 |  |
| yes | Brian Parshall | `bjp8w` | G. T. Whyburn Professor | 2017-06-19--2020-08-20 |  |
| yes | Karen Parshall | `khp3k` | Commonwealth Professor of Mathematics and History | 2017-06-19--2023-08-15 |  |
| yes | Leonid Petrov | `lap5r` | Associate Professor | 2019-07-27--2024-08-20 |  |
| yes | You Qi | `yq2dw` | Assistant Professor | 2019-08-21--2025-08-26 |  |
| yes | Andrei Rapinchuk | `asr3x` | McConnell-Bernard Professor of Mathematics | 2017-06-19--open |  |
| yes | Christian Reidys | `cmr3hk` | Professor | 2018-12-19--open |  |
| yes | David Sherman | `des5e` | Associate Professor | 2017-06-19--open |  |
| yes | Weiqiang Wang | `ww9c` | Professor | 2017-06-19--2020-09-17 |  |

## Snapshot detail: Start AY 2021-22 (2021-08-01)

Git-only count: 29. Adjusted active-TT count: 29.

| Count? | Person | UVA id | Position in git interval | Interval | Note |
|---|---|---|---|---|---|
| yes | Abdelmalek Abdesselam | `aa4cr` | Associate Professor | 2017-05-10--open |  |
| yes | Peter Abramenko | `pa8e` | Professor | 2017-06-19--open |  |
| yes | Julie Bergner | `jeb2md` | Professor | 2019-07-27--2023-08-22 |  |
| yes | Yen Do | `yqd3p` | Associate Professor | 2020-08-20--open |  |
| yes | Mikhail Ershov | `mve2x` | Professor | 2018-08-30--open |  |
| yes | Juraj Földes | `jf8dc` | Assistant Professor | 2017-06-19--2022-06-09 |  |
| yes | Evangelia Gazaki | `eg4va` | Assistant Professor | 2019-08-20--2025-08-26 |  |
| yes | Christian Gromoll | `hcg3m` | Associate Professor | 2017-05-06--open |  |
| yes | Zoran Grujic | `zg7c` | Professor | 2018-08-29--2023-08-15 |  |
| yes | Benjamin Hayes | `brh5c` | Assistant Professor | 2017-08-04--2022-06-09 |  |
| yes | Ira Herbst | `iwh` | Professor and Associate Chair | 2019-08-23--2021-08-20 |  |
| yes | Peter Humphries | `ph7ph` | Assistant Professor | 2020-08-25--open |  |
| yes | Craig Huneke | `clh4xd` | Marvin Rosenblum Professor | 2017-08-04--2022-07-31 |  |
| yes | John Imbrie | `ji2k` | Professor & Chair | 2018-08-29--2021-08-20 |  |
| yes | Thomas Koberda | `tmk5a` | Associate Professor | 2019-07-27--2022-08-08 |  |
| yes | Slava Krushkal | `vk6e` | Professor | 2019-08-23--open |  |
| yes | Nicholas Kuhn | `njk4x` | Professor | 2017-06-19--2024-07-31 |  |
| yes | Sara Maloni | `sm4cw` | Assistant Professor | 2017-06-19--2022-06-09 |  |
| yes | Thomas Mark | `tmark` | Professor | 2019-07-27--2021-08-20 |  |
| yes | Tai Melcher | `tam7b` | Associate Professor | 2017-06-19--open |  |
| yes | Jennifer Morse | `jlm6cj` | Professor | 2017-05-06--open |  |
| yes | Ken Ono | `ko5wk` | Thomas Jefferson Professor of Mathematics | 2019-07-27--2021-08-20 |  |
| yes | Karen Parshall | `khp3k` | Commonwealth Professor of Mathematics and History | 2017-06-19--2023-08-15 |  |
| yes | Leonid Petrov | `lap5r` | Associate Professor | 2019-07-27--2024-08-20 |  |
| yes | You Qi | `yq2dw` | Assistant Professor | 2019-08-21--2025-08-26 |  |
| yes | Andrei Rapinchuk | `asr3x` | McConnell-Bernard Professor of Mathematics | 2017-06-19--open |  |
| yes | Christian Reidys | `cmr3hk` | Professor | 2018-12-19--open |  |
| yes | David Sherman | `des5e` | Associate Professor | 2017-06-19--open |  |
| yes | Weiqiang Wang | `ww9c` | Gordon Whyburn Professor of Mathematics | 2020-09-17--open |  |

## Snapshot detail: Start AY 2022-23 (2022-08-01)

Git-only count: 27. Adjusted active-TT count: 27.

| Count? | Person | UVA id | Position in git interval | Interval | Note |
|---|---|---|---|---|---|
| yes | Abdelmalek Abdesselam | `aa4cr` | Associate Professor | 2017-05-10--open |  |
| yes | Peter Abramenko | `pa8e` | Professor | 2017-06-19--open |  |
| yes | Julie Bergner | `jeb2md` | Professor | 2019-07-27--2023-08-22 |  |
| yes | Yen Do | `yqd3p` | Associate Professor | 2020-08-20--open |  |
| yes | Mikhail Ershov | `mve2x` | Professor | 2018-08-30--open |  |
| yes | Juraj Földes | `jf8dc` | Associate Professor | 2022-06-09--open |  |
| yes | Evangelia Gazaki | `eg4va` | Assistant Professor | 2019-08-20--2025-08-26 |  |
| yes | Christian Gromoll | `hcg3m` | Associate Professor | 2017-05-06--open |  |
| yes | Zoran Grujic | `zg7c` | Professor | 2018-08-29--2023-08-15 |  |
| yes | Benjamin Hayes | `brh5c` | Associate Professor | 2022-06-09--open |  |
| yes | Peter Humphries | `ph7ph` | Assistant Professor | 2020-08-25--open |  |
| yes | John Imbrie | `ji2k` | Professor | 2021-08-20--2022-12-22 |  |
| yes | Thomas Koberda | `tmk5a` | Associate Professor | 2019-07-27--2022-08-08 |  |
| yes | Slava Krushkal | `vk6e` | Professor | 2019-08-23--open |  |
| yes | Nicholas Kuhn | `njk4x` | Professor | 2017-06-19--2024-07-31 |  |
| yes | Sara Maloni | `sm4cw` | Associate Professor | 2022-06-09--open |  |
| yes | Thomas Mark | `tmark` | Professor and Associate Chair | 2021-08-20--2022-08-08 |  |
| yes | Tai Melcher | `tam7b` | Associate Professor | 2017-06-19--open |  |
| yes | Jennifer Morse | `jlm6cj` | Professor | 2017-05-06--open |  |
| yes | Ken Ono | `ko5wk` | Chairman and Marvin Rosenblum Professor of Mathematics | 2022-07-31--2022-12-22 |  |
| yes | Karen Parshall | `khp3k` | Commonwealth Professor of Mathematics and History | 2017-06-19--2023-08-15 |  |
| yes | Leonid Petrov | `lap5r` | Associate Professor | 2019-07-27--2024-08-20 |  |
| yes | You Qi | `yq2dw` | Assistant Professor | 2019-08-21--2025-08-26 |  |
| yes | Andrei Rapinchuk | `asr3x` | McConnell-Bernard Professor of Mathematics | 2017-06-19--open |  |
| yes | Christian Reidys | `cmr3hk` | Professor | 2018-12-19--open |  |
| yes | David Sherman | `des5e` | Associate Professor | 2017-06-19--open |  |
| yes | Weiqiang Wang | `ww9c` | Gordon Whyburn Professor of Mathematics | 2020-09-17--open |  |

## Snapshot detail: Start AY 2023-24 (2023-08-01)

Git-only count: 27. Adjusted active-TT count: 27.

| Count? | Person | UVA id | Position in git interval | Interval | Note |
|---|---|---|---|---|---|
| yes | Abdelmalek Abdesselam | `aa4cr` | Associate Professor | 2017-05-10--open |  |
| yes | Peter Abramenko | `pa8e` | Professor | 2017-06-19--open |  |
| yes | Julie Bergner | `jeb2md` | Professor | 2019-07-27--2023-08-22 |  |
| yes | Yen Do | `yqd3p` | Associate Professor | 2020-08-20--open |  |
| yes | Mikhail Ershov | `mve2x` | Professor | 2018-08-30--open |  |
| yes | Juraj Földes | `jf8dc` | Associate Professor | 2022-06-09--open |  |
| yes | Evangelia Gazaki | `eg4va` | Assistant Professor | 2019-08-20--2025-08-26 |  |
| yes | Christian Gromoll | `hcg3m` | Associate Professor | 2017-05-06--open |  |
| yes | Zoran Grujic | `zg7c` | Professor | 2018-08-29--2023-08-15 |  |
| yes | Benjamin Hayes | `brh5c` | Associate Professor | 2022-06-09--open |  |
| yes | Peter Humphries | `ph7ph` | Assistant Professor | 2020-08-25--open |  |
| yes | John Imbrie | `ji2k` | Interim Chair and Professor | 2022-12-22--2023-08-15 |  |
| yes | Thomas Koberda | `tmk5a` | Associate Professor and Associate Chair | 2022-08-08--2023-08-21 |  |
| yes | Slava Krushkal | `vk6e` | Professor | 2019-08-23--open |  |
| yes | Nicholas Kuhn | `njk4x` | Professor | 2017-06-19--2024-07-31 |  |
| yes | Sara Maloni | `sm4cw` | Associate Professor | 2022-06-09--open |  |
| yes | Thomas Mark | `tmark` | Professor | 2022-08-08--2023-08-15 |  |
| yes | Tai Melcher | `tam7b` | Associate Professor | 2017-06-19--open |  |
| yes | Jennifer Morse | `jlm6cj` | Professor | 2017-05-06--open |  |
| yes | Ken Ono | `ko5wk` | STEM Advisor to the Provost and Marvin Rosenblum Professor of Mathematics | 2022-12-22--open |  |
| yes | Karen Parshall | `khp3k` | Commonwealth Professor of Mathematics and History | 2017-06-19--2023-08-15 |  |
| yes | Leonid Petrov | `lap5r` | Associate Professor | 2019-07-27--2024-08-20 |  |
| yes | You Qi | `yq2dw` | Assistant Professor | 2019-08-21--2025-08-26 |  |
| yes | Andrei Rapinchuk | `asr3x` | McConnell-Bernard Professor of Mathematics | 2017-06-19--open |  |
| yes | Christian Reidys | `cmr3hk` | Professor | 2018-12-19--open |  |
| yes | David Sherman | `des5e` | Associate Professor | 2017-06-19--open |  |
| yes | Weiqiang Wang | `ww9c` | Gordon Whyburn Professor of Mathematics | 2020-09-17--open |  |

## Snapshot detail: Start AY 2024-25 (2024-08-01)

Git-only count: 26. Adjusted active-TT count: 26.

| Count? | Person | UVA id | Position in git interval | Interval | Note |
|---|---|---|---|---|---|
| yes | Abdelmalek Abdesselam | `aa4cr` | Associate Professor | 2017-05-10--open |  |
| yes | Peter Abramenko | `pa8e` | Professor | 2017-06-19--open |  |
| yes | Julie Bergner | `jeb2md` | Professor and Associate Chair | 2023-08-22--2024-11-14 |  |
| yes | Yen Do | `yqd3p` | Associate Professor | 2020-08-20--open |  |
| yes | Mikhail Ershov | `mve2x` | Professor | 2018-08-30--open |  |
| yes | Aseel Farhat | `af7py` | Assistant Professor | 2024-07-31--2025-08-26 |  |
| yes | Juraj Földes | `jf8dc` | Associate Professor | 2022-06-09--open |  |
| yes | Evangelia Gazaki | `eg4va` | Assistant Professor | 2019-08-20--2025-08-26 |  |
| yes | Christian Gromoll | `hcg3m` | Associate Professor | 2017-05-06--open |  |
| yes | Benjamin Hayes | `brh5c` | Associate Professor | 2022-06-09--open |  |
| yes | Peter Humphries | `ph7ph` | Assistant Professor | 2020-08-25--open |  |
| yes | John Imbrie | `ji2k` | Professor | 2023-08-15--open |  |
| yes | Thomas Koberda | `tmk5a` | Professor | 2023-08-21--open |  |
| yes | Slava Krushkal | `vk6e` | Professor | 2019-08-23--open |  |
| yes | Sara Maloni | `sm4cw` | Associate Professor | 2022-06-09--open |  |
| yes | Thomas Mark | `tmark` | Professor and Chair | 2023-08-15--open |  |
| yes | Tai Melcher | `tam7b` | Associate Professor | 2017-06-19--open |  |
| yes | Jennifer Morse | `jlm6cj` | Professor | 2017-05-06--open |  |
| yes | Ken Ono | `ko5wk` | STEM Advisor to the Provost and Marvin Rosenblum Professor of Mathematics | 2022-12-22--open |  |
| yes | Leonid Petrov | `lap5r` | Associate Professor | 2019-07-27--2024-08-20 |  |
| yes | You Qi | `yq2dw` | Assistant Professor | 2019-08-21--2025-08-26 |  |
| yes | J.D. Quigley | `mbp6pj` | Assistant Professor | 2023-08-15--open |  |
| yes | Andrei Rapinchuk | `asr3x` | McConnell-Bernard Professor of Mathematics | 2017-06-19--open |  |
| yes | Christian Reidys | `cmr3hk` | Professor | 2018-12-19--open |  |
| yes | David Sherman | `des5e` | Associate Professor | 2017-06-19--open |  |
| yes | Weiqiang Wang | `ww9c` | Gordon Whyburn Professor of Mathematics | 2020-09-17--open |  |

## Snapshot detail: Start AY 2025-26 (2025-08-01)

Git-only count: 26. Adjusted active-TT count: 26.

| Count? | Person | UVA id | Position in git interval | Interval | Note |
|---|---|---|---|---|---|
| yes | Abdelmalek Abdesselam | `aa4cr` | Associate Professor | 2017-05-10--open |  |
| yes | Peter Abramenko | `pa8e` | Professor | 2017-06-19--open |  |
| yes | Julie Bergner | `jeb2md` | Professor | 2024-11-14--open |  |
| yes | Yen Do | `yqd3p` | Associate Professor | 2020-08-20--open |  |
| yes | Mikhail Ershov | `mve2x` | Professor | 2018-08-30--open |  |
| yes | Aseel Farhat | `af7py` | Assistant Professor | 2024-07-31--2025-08-26 |  |
| yes | Juraj Földes | `jf8dc` | Associate Professor | 2022-06-09--open |  |
| yes | Evangelia Gazaki | `eg4va` | Assistant Professor | 2019-08-20--2025-08-26 |  |
| yes | Christian Gromoll | `hcg3m` | Associate Professor | 2017-05-06--open |  |
| yes | Benjamin Hayes | `brh5c` | Associate Professor | 2022-06-09--open |  |
| yes | Peter Humphries | `ph7ph` | Assistant Professor | 2020-08-25--open |  |
| yes | John Imbrie | `ji2k` | Professor | 2023-08-15--open |  |
| yes | Thomas Koberda | `tmk5a` | Professor | 2023-08-21--open |  |
| yes | Slava Krushkal | `vk6e` | Professor | 2019-08-23--open |  |
| yes | Sara Maloni | `sm4cw` | Associate Professor | 2022-06-09--open |  |
| yes | Thomas Mark | `tmark` | Professor and Chair | 2023-08-15--open |  |
| yes | Tai Melcher | `tam7b` | Associate Professor | 2017-06-19--open |  |
| yes | Jennifer Morse | `jlm6cj` | Professor | 2017-05-06--open |  |
| yes | Ken Ono | `ko5wk` | STEM Advisor to the Provost and Marvin Rosenblum Professor of Mathematics | 2022-12-22--open |  |
| yes | Leonid Petrov | `lap5r` | Professor | 2024-08-20--open |  |
| yes | You Qi | `yq2dw` | Assistant Professor | 2019-08-21--2025-08-26 |  |
| yes | J.D. Quigley | `mbp6pj` | Assistant Professor | 2023-08-15--open |  |
| yes | Andrei Rapinchuk | `asr3x` | McConnell-Bernard Professor of Mathematics | 2017-06-19--open |  |
| yes | Christian Reidys | `cmr3hk` | Professor | 2018-12-19--open |  |
| yes | David Sherman | `des5e` | Associate Professor | 2017-06-19--open |  |
| yes | Weiqiang Wang | `ww9c` | Gordon Whyburn Professor of Mathematics | 2020-09-17--open |  |

## Snapshot detail: Ono leave begins (2026-01-01)

Git-only count: 26. Adjusted active-TT count: 25.

| Count? | Person | UVA id | Position in git interval | Interval | Note |
|---|---|---|---|---|---|
| yes | Abdelmalek Abdesselam | `aa4cr` | Associate Professor | 2017-05-10--open |  |
| yes | Peter Abramenko | `pa8e` | Professor | 2017-06-19--open |  |
| yes | Julie Bergner | `jeb2md` | Professor | 2024-11-14--open |  |
| yes | Yen Do | `yqd3p` | Associate Professor | 2020-08-20--open |  |
| yes | Mikhail Ershov | `mve2x` | Professor | 2018-08-30--open |  |
| yes | Aseel Farhat | `af7py` | Associate Professor | 2025-08-26--open |  |
| yes | Juraj Földes | `jf8dc` | Associate Professor | 2022-06-09--open |  |
| yes | Evangelia Gazaki | `eg4va` | Associate Professor | 2025-08-26--open |  |
| yes | Christian Gromoll | `hcg3m` | Associate Professor | 2017-05-06--open |  |
| yes | Benjamin Hayes | `brh5c` | Associate Professor | 2022-06-09--open |  |
| yes | Peter Humphries | `ph7ph` | Assistant Professor | 2020-08-25--open |  |
| yes | John Imbrie | `ji2k` | Professor | 2023-08-15--open |  |
| yes | Thomas Koberda | `tmk5a` | Professor | 2023-08-21--open |  |
| yes | Slava Krushkal | `vk6e` | Professor | 2019-08-23--open |  |
| yes | Sara Maloni | `sm4cw` | Associate Professor | 2022-06-09--open |  |
| yes | Thomas Mark | `tmark` | Professor and Chair | 2023-08-15--open |  |
| yes | Tai Melcher | `tam7b` | Associate Professor | 2017-06-19--open |  |
| yes | Jennifer Morse | `jlm6cj` | Professor | 2017-05-06--open |  |
| no | Ken Ono | `ko5wk` | STEM Advisor to the Provost and Marvin Rosenblum Professor of Mathematics | 2022-12-22--open | exclude active TT: extended leave since Jan 2026; return uncertain |
| yes | Leonid Petrov | `lap5r` | Professor | 2024-08-20--open |  |
| yes | You Qi | `yq2dw` | Associate Professor | 2025-08-26--open |  |
| yes | J.D. Quigley | `mbp6pj` | Assistant Professor | 2023-08-15--open |  |
| yes | Andrei Rapinchuk | `asr3x` | McConnell-Bernard Professor of Mathematics | 2017-06-19--open |  |
| yes | Christian Reidys | `cmr3hk` | Professor | 2018-12-19--open |  |
| yes | David Sherman | `des5e` | Associate Professor | 2017-06-19--open |  |
| yes | Weiqiang Wang | `ww9c` | Gordon Whyburn Professor of Mathematics | 2020-09-17--open |  |

## Snapshot detail: As-of 2026-06-02 (2026-06-02)

Git-only count: 26. Adjusted active-TT count: 24.

| Count? | Person | UVA id | Position in git interval | Interval | Note |
|---|---|---|---|---|---|
| yes | Abdelmalek Abdesselam | `aa4cr` | Associate Professor | 2017-05-10--open |  |
| yes | Peter Abramenko | `pa8e` | Professor | 2017-06-19--open |  |
| yes | Julie Bergner | `jeb2md` | Professor | 2024-11-14--open |  |
| yes | Yen Do | `yqd3p` | Associate Professor | 2020-08-20--open |  |
| yes | Mikhail Ershov | `mve2x` | Professor | 2018-08-30--open |  |
| yes | Aseel Farhat | `af7py` | Associate Professor | 2025-08-26--open |  |
| yes | Juraj Földes | `jf8dc` | Associate Professor | 2022-06-09--open |  |
| yes | Evangelia Gazaki | `eg4va` | Associate Professor | 2025-08-26--open |  |
| yes | Christian Gromoll | `hcg3m` | Associate Professor | 2017-05-06--open |  |
| yes | Benjamin Hayes | `brh5c` | Associate Professor | 2022-06-09--open |  |
| yes | Peter Humphries | `ph7ph` | Assistant Professor | 2020-08-25--open |  |
| no | John Imbrie | `ji2k` | Professor | 2023-08-15--open | exclude active TT: retired spring/summer 2026 |
| yes | Thomas Koberda | `tmk5a` | Professor | 2023-08-21--open |  |
| yes | Slava Krushkal | `vk6e` | Professor | 2019-08-23--open |  |
| yes | Sara Maloni | `sm4cw` | Associate Professor | 2022-06-09--open |  |
| yes | Thomas Mark | `tmark` | Professor and Chair | 2023-08-15--open |  |
| yes | Tai Melcher | `tam7b` | Associate Professor | 2017-06-19--open |  |
| yes | Jennifer Morse | `jlm6cj` | Professor | 2017-05-06--open |  |
| no | Ken Ono | `ko5wk` | STEM Advisor to the Provost and Marvin Rosenblum Professor of Mathematics | 2022-12-22--open | exclude active TT: extended leave since Jan 2026; return uncertain |
| yes | Leonid Petrov | `lap5r` | Professor | 2024-08-20--open |  |
| yes | You Qi | `yq2dw` | Associate Professor | 2025-08-26--open |  |
| yes | J.D. Quigley | `mbp6pj` | Assistant Professor | 2023-08-15--open |  |
| yes | Andrei Rapinchuk | `asr3x` | McConnell-Bernard Professor of Mathematics | 2017-06-19--open |  |
| yes | Christian Reidys | `cmr3hk` | Professor | 2018-12-19--open |  |
| yes | David Sherman | `des5e` | Associate Professor | 2017-06-19--open |  |
| yes | Weiqiang Wang | `ww9c` | Gordon Whyburn Professor of Mathematics | 2020-09-17--open |  |

## Snapshot detail: Fall 2026 report endpoint (2026-08-01)

Git-only count: 26. Adjusted active-TT count: 24.

| Count? | Person | UVA id | Position in git interval | Interval | Note |
|---|---|---|---|---|---|
| yes | Abdelmalek Abdesselam | `aa4cr` | Associate Professor | 2017-05-10--open |  |
| yes | Peter Abramenko | `pa8e` | Professor | 2017-06-19--open |  |
| yes | Julie Bergner | `jeb2md` | Professor | 2024-11-14--open |  |
| yes | Yen Do | `yqd3p` | Associate Professor | 2020-08-20--open |  |
| yes | Mikhail Ershov | `mve2x` | Professor | 2018-08-30--open |  |
| yes | Aseel Farhat | `af7py` | Associate Professor | 2025-08-26--open |  |
| yes | Juraj Földes | `jf8dc` | Associate Professor | 2022-06-09--open |  |
| yes | Evangelia Gazaki | `eg4va` | Associate Professor | 2025-08-26--open |  |
| yes | Christian Gromoll | `hcg3m` | Associate Professor | 2017-05-06--open |  |
| yes | Benjamin Hayes | `brh5c` | Associate Professor | 2022-06-09--open |  |
| yes | Peter Humphries | `ph7ph` | Assistant Professor | 2020-08-25--open |  |
| no | John Imbrie | `ji2k` | Professor | 2023-08-15--open | exclude active TT: retired spring/summer 2026 |
| yes | Thomas Koberda | `tmk5a` | Professor | 2023-08-21--open |  |
| yes | Slava Krushkal | `vk6e` | Professor | 2019-08-23--open |  |
| yes | Sara Maloni | `sm4cw` | Associate Professor | 2022-06-09--open |  |
| yes | Thomas Mark | `tmark` | Professor and Chair | 2023-08-15--open |  |
| yes | Tai Melcher | `tam7b` | Associate Professor | 2017-06-19--open |  |
| yes | Jennifer Morse | `jlm6cj` | Professor | 2017-05-06--open |  |
| no | Ken Ono | `ko5wk` | STEM Advisor to the Provost and Marvin Rosenblum Professor of Mathematics | 2022-12-22--open | exclude active TT: extended leave since Jan 2026; return uncertain |
| yes | Leonid Petrov | `lap5r` | Professor | 2024-08-20--open |  |
| yes | You Qi | `yq2dw` | Associate Professor | 2025-08-26--open |  |
| yes | J.D. Quigley | `mbp6pj` | Assistant Professor | 2023-08-15--open |  |
| yes | Andrei Rapinchuk | `asr3x` | McConnell-Bernard Professor of Mathematics | 2017-06-19--open |  |
| yes | Christian Reidys | `cmr3hk` | Professor | 2018-12-19--open |  |
| yes | David Sherman | `des5e` | Associate Professor | 2017-06-19--open |  |
| yes | Weiqiang Wang | `ww9c` | Gordon Whyburn Professor of Mathematics | 2020-09-17--open |  |

## Historical parser triage

Current generated data has **0 `history_parse_error` notices**.

The old newline-only placeholder commits (for example, an initial `Create vz6an.md` followed by a same-day `Update vz6an.md` with the actual profile) are now skipped rather than surfaced as roster issues. They are not current empty files and not parser failures.
