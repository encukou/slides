\ProvidesClass{pyslides}
\LoadClass{beamer}

\usepackage[utf8x]{inputenc}
\usepackage{url}
\usepackage{pgf}
\usepackage{tikz}

\usepackage{palatino}
\usepackage{tgpagella}

\usepackage{textcomp}
\usepackage{color}

\newcommand\py@slidenumber{}
\newcommand\py@slidenumber@{}
\newcommand\pyslidenumber[1]{\global\renewcommand\py@slidenumber@{#1. }\global\renewcommand\py@slidenumber{#1}}
\newcommand\insertframetitle{}

\defbeamertemplate*{footline}{python}
{
  \leavevmode%
  \hbox{%
  \begin{beamercolorbox}[wd=.333333\paperwidth,ht=2.25ex,dp=1ex,center]{author in head/foot}%
    \usebeamerfont{author in head/foot}Python Seminar
  \end{beamercolorbox}%
  \begin{beamercolorbox}[wd=.333333\paperwidth,ht=2.25ex,dp=1ex,center]{title in head/foot}%
    \usebeamerfont{title in head/foot}\py@slidenumber@\insertshorttitle
  \end{beamercolorbox}%
  \begin{beamercolorbox}[wd=.333333\paperwidth,ht=2.25ex,dp=1ex,right]{date in head/foot}%
    \usebeamerfont{date in head/foot}\insertshortdate{}\hspace*{2em}
    \insertframenumber{} / \inserttotalframenumber\hspace*{2ex} 
  \end{beamercolorbox}}%
  \vskip0pt%
}

\defbeamertemplate*{headline}{python}
{%
  \leavevmode%
  \begin{beamercolorbox}[wd=.666\paperwidth,ht=2.5ex,dp=1.125ex]{section in head/foot}%
    \insertsectionnavigationhorizontal{.5\paperwidth}{\hskip0pt plus1filll}{}%
  \end{beamercolorbox}%
  \begin{beamercolorbox}[wd=.334\paperwidth,ht=2.5ex,dp=1.125ex]{subsection in head/foot}%
    \hfill
  \end{beamercolorbox}%
}

\defbeamertemplate*{title page}{python}[1][]
{
  \vbox{}
  \vfill
  \begin{centering}
        {\usebeamerfont{institute}Python Seminar, part \py@slidenumber}
        \vskip0.25em%
    \includegraphics[height=3em]{logo-only}
    \vskip0.25em%
    \begin{beamercolorbox}[sep=8pt,center,#1]{title}
      \usebeamerfont{title}\inserttitle\par%
    \end{beamercolorbox}%
    \vskip1em\par
    \begin{beamercolorbox}[sep=8pt,center,#1]{author}
      \usebeamerfont{author}\insertauthor
    \end{beamercolorbox}
    \begin{beamercolorbox}[sep=8pt,center,#1]{institute}
      \usebeamerfont{institute}\insertinstitute
    \end{beamercolorbox}
    \begin{beamercolorbox}[sep=8pt,center,#1]{date}
      \usebeamerfont{date}\insertdate
    \end{beamercolorbox}\vskip0.5em
    {\usebeamercolor[fg]{titlegraphic}\inserttitlegraphic\par}
    \vskip3em%
  \end{centering}
  \vfill
}

\defbeamertemplate*{frametitle}{python}
{%
  \nointerlineskip%
    \ifx\insertframetitle\@empty%
    \else%
    \subsection{\insertframetitle}%
    \fi%
  \vskip-2pt%
  \hbox{\leavevmode
    \advance\beamer@leftmargin by -12bp%
    \advance\beamer@rightmargin by -12bp%
    \beamer@tempdim=\textwidth%
    \advance\beamer@tempdim by \beamer@leftmargin%
    \advance\beamer@tempdim by \beamer@rightmargin%
    \hskip-\Gm@lmargin\hbox{%
      \setbox\beamer@tempbox=\hbox{\begin{minipage}[b]{\paperwidth}%
          \vbox{}\vskip-.75ex%
          \leftskip0.3cm%
          \rightskip0.3cm plus1fil\leavevmode
          \insertframetitle%
          \ifx\insertframesubtitle\@empty%
            \strut\par%
          \else
            \par{\usebeamerfont*{framesubtitle}{\usebeamercolor[fg]{framesubtitle}\insertframesubtitle}\strut\par}%
          \fi%
          \nointerlineskip
          \vbox{}%
          \end{minipage}}%
      \beamer@tempdim=\ht\beamer@tempbox%
      \advance\beamer@tempdim by 2pt%
      \begin{pgfpicture}{0pt}{0pt}{\paperwidth}{\beamer@tempdim}
        \usebeamercolor{frametitle right}
        \pgfpathrectangle{\pgfpointorigin}{\pgfpoint{\paperwidth}{\beamer@tempdim}}
        \pgfusepath{clip}
        \pgftext[left,base]{\pgfuseshading{beamer@frametitleshade}}
      \end{pgfpicture}
      \hskip-\paperwidth%
      \box\beamer@tempbox%
    }%
    \hskip-\Gm@rmargin%
  }%
  \nointerlineskip
    \vskip-0.2pt
    \hbox to\textwidth{\hskip-\Gm@lmargin\pgfuseshading{beamer@topshade}\hskip-\Gm@rmargin}
    \vskip-2pt
    \tikz[remember picture,overlay]
      \node[xshift=0.125ex,yshift=0.125ex,anchor=north east] (n)
      at (current page.north east)
      {\includegraphics[height=4.6ex]{logo-only}};
    \vskip-0.5cm
}

\useinnertheme[shadow=true]{rounded}
\useoutertheme{shadow}
\usecolortheme{whale}
\usecolortheme{orchid}

\DeclareOptionBeamer{reference}{\setbeamercolor{structure}{fg=red!20!yellow!95!blue!90!black}}
\ProcessOptionsBeamer


\setbeamerfont{block title}{size={}}

\setbeamertemplate{title page}[python][colsep=-4bp,rounded=true,shadow=\beamer@themerounded@shadow]
\setbeamertemplate{footline}[python]
\setbeamertemplate{headline}[python]
\setbeamertemplate{frametitle}[python]

\setbeamertemplate{navigation symbols}{}

\hypersetup{author=Petr Viktorin}

\author{Petr Viktorin}
\institute{University of Eastern Finland}

\newcommand\gobble[1]{}
\newcommand\magic[1]{\_\_#1\_\_}

\makeatletter
\let \@sverbatim \@verbatim
\def \@verbatim {\@sverbatim \verbatimplus}
{
    \catcode`'=13 \catcode`"=13 \gdef \verbatimplus{\catcode`'=13 \chardef '=13 \catcode`"=13 \chardef "=34 } 
} 
\makeatother

% \AtBeginSection[] {
%   \begin{frame}<beamer>
%     \frametitle{Contents}
%     \tableofcontents[currentsection,currentsubsection]
%   \end{frame}
% }

\definecolor{silver}{rgb}{0.8,0.8,0.8}

\usepackage{fancyvrb}

\input "|./highlight.py"
