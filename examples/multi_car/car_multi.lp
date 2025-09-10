#const n = 8.
#const c = 4.
car(1..c).
time(0..n).        step(I,I+1) :- time(I), I < n.
budget(10000).
delta(10).

&sus {acc(C,I) :: acc(C,I) : car(C), time(I)} <= X :- budget(X).
:- &sus {acc(C,I)} = 0, car(C), time(I).

&sus {s(C,0)} = 0  :- car(C).
:- &sus {s(C,I) }>  200, car(C), time(I).  % max speed limit
:- &sus {s(C,I) }< -200, car(C), time(I).  % min speed limit
&sus {s(C,I)+acc(C,I')} =: s(C,I') :- acc(C,I'), step(I,I').

&sus {s(C,I)} =: s(C,I') :- not &sus{ s(C,I') } != s(C,I), car(C), step(I,I').

&sus {p(C,0)} = 0 :- car(C).
&sus {p(C,I)+s(C,I)} =: p(C,I') :- step(I,I'), car(C).

&sus {p(C,n)-p(C',n)} <= D :- car(C), car(C'), delta(D), &sus {p(C,n)} <= p(C',n).  % goal position

#show acc/2.