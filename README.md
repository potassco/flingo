# flingo

flingo is a solver for ASP modulo conditional linear constraints with founded variables.

## Installation

Requires `python>=3.12` and `pip`.

To install from PyPI:
```shell
pip install flingo
```

To install without checking out the repository:
```shell
pip install git+https://github.com/potassco/flingo.git
```

To install from repository root:
```shell
pip install .
```

## Usage

flingo is a solver for Answer Set Programming (ASP) combined with founded conditional linear constraints. These constraints enable the user to use integer variables that are not subject to grounding. Integer variables may be undefined and, in line with the philosophy of ASP, there needs to be a justification in the logic program if a variable receives a value in an answer set. Conditionality allows for a generalization of aggregates commonly used in ASP.

### Relation to clingo
flingo is an extension of [clingo](https://github.com/potassco/clingo) and accepts as input clingo rules enriched with founded conditional linear constraints. 

### Relation to clingcon
flingo relies on the constraint answer set programming (CASP) solver [clingcon](https://github.com/potassco/clingo) into whose language a flingo program is translated. flingo's two main advantages are foundedness of the integer variables and aggregates over integer variables. The former allows variables to be undefined and only assume a value if a reason for that value can be derived. This differs to the behavior of CASP, where variables are always defined and in absence of any constraint to a variable, all possible values are enumerated. The latter generalizes ASP aggregates to contain integer variables that are not subject to grounding.

### Output
The answer sets of flingo programs contain terms `val(x,v)`, where `x` is an integer variable occurring in the program and `v` is the integer value of the variable in the answer set. The absence of such a term means the variable is undefined.

### Language overview
flingo atoms have the following form:
1. `&sum{lt1 : c1;...;ltn : cn} <> l0`
2. `&sus{lt1 : c1;...;ltn : cn} <> l0` 
3. `&in{lb..ub} =: x`
4. `&df{x}`
5. `&min{lt1 : c1;...;ltn : cn} <> l0`
6. `&max{lt1 : c1;...;ltn : cn} <> l0`

where `lti`, `lb`, and `ub` are linear terms,
`ci` is a conjunction of literals for `i` between 0 and `n`, `x` is the name of a variable and `<>` is either `<=`,`=`,`!=`,`<`,`>`, or `>=`.

To hide and show assignments of specific variables, one can use the directive `&show{v1/a1;...;vn/an}`, where `vi` is the name of the function and `ai` is the arity of the function. For instance, the term `x/0` shows the variable named `x` while `price/1` shows all variables of the form `price(<argument>)`. Absence of this directive shows all variables, and `&show{}` hides all variables.

### 1. Sum under clingo semantics
The atom in 1. sums up all linear terms in the set. It can be seen as a generalization of clingo sum aggregates as it similarly removes undefined elements, and therefore always returns a value. It can be used in the head and in the body.

For example,
```
price(frame,15).
price(bag,5).

  selected(frame).
{ selected(bag) }.

&sum{V} = price(P) :- selected(P), price(P,V).
&sum{price(P) : selected(P)} = price(total).

#show selected/1.
&show{price/1}.
```
This program configures a bike with a frame that has an optional bag. For both the frame and the optional bag prices are provided, stored in integer variables and then summed up to get the total price.

Executing 
```shell
flingo examples/config_optional.lp
```
yields the answer sets
```
Answer: 1
selected(frame) val(price(total),15) val(price(frame),15)
Answer: 2
selected(frame) selected(bag) val(price(bag),5) val(price(total),20) val(price(frame),15)
```
As expected, we have two answer sets. The first does not select the optional bag and calculates the total price as 15, same as the price of the frame. The second selects the bag and increases the total price to 20.

To see the behavior in presence of undefined integer variables, consider following example
```
price(frame,15).

pricelimit(14).

  selected(frame).
{ selected(bag) }.

&sum{V} = price(P) :- selected(P), price(P,V).
:- &sum { price(P) : selected(P)  } >= L,
   pricelimit(L).

#show selected/1.
&show{price/1}.
```
Now, the price of the bag is omitted and instead of calculating the total price, we restrict the sum over the individual prices to be 14.
The call
```
flingo examples/config_pricelimit_sum.lp 0
```
returns
```
UNSATISFIABLE
```
Even if the price for the bag is undefined, the constraint detects that the price limit is breached since the undefined integer variable is removed from the set.

### 2. Sum under strict semantics

The atom in 2. sums up the linear terms for the conditions that are true. In contrast to 1., if any of the terms is undefined, resulting from an integer variable being undefined that is contained within, the sum is undefined as well. This results in the atom being false. We will later elaborate how this version of sum is useful for assignments later in this document. The atom may be used in the head or in the body.

The example `examples/config_optional.lp` behaves identically when we replace `sus` with `sum`.

Different behavior arises for the price limit.
```
price(frame,15).

pricelimit(14).

  selected(frame).
{ selected(bag) }.

&sus{V} = price(P) :- selected(P), price(P,V).
:- &sus { price(P) : selected(P)  } >= L,
   pricelimit(L).

#show selected/1.
&show{price/1}.
```

The call
```
flingo examples/config_pricelimit_sus.lp 0
```
now returns
```
Answer: 1
selected(frame) selected(bag) val(price(frame),15)
```
The answer with only the frame is removed because its price alone is higher than the limit.
However, when the bag is selected, its price value is undefined and therefore the sum under strict semantics returns undefined as well and the price limit is disregarded.

### 3. Assignments

The atom in 3. is a directional assignment of a value between linear terms `lb` and `ub` to the variable `x`. It may only be used in the head of a rule. Only if `lb` and `ub` are defined, `x` will receive a value in between `lb` and `ub`. Note that this is different from using equality to assign a value. For instance, the fact `&sus{y}=x.` would allow `y` as well as `x` to be defined and take on arbitrary values such that `x` and `y` are equal, while `&in{y..y}=:x.` requires some other rule to define `y` and if that is not the case, `x` remains undefined. 
One can also use the strict sum and write `&sus{lt1 : c1;..;ltn : cn}=:x`, where `lti` are linear terms conditioned by conjuctions `ci` for `i` between 1 and `n`, and `x` is an integer variable. Using the strict sum that way has two advantages: first, the strict sum can be undefined in contrast to the clingo sum and thefore `x` only receives a value if the strict sum can be calculated, and second, the linear terms may be conditioned and the arity of the sum can be arbitrary. 

For instance, take program
```
price(frame,15).
default_range(1,2).

  selected(frame).
{ selected(bag) }.

&sus{V} = price(P)    :- selected(P), price(P,V).
&in{L..U} =: price(P) :- selected(P), not price(P,_), 
                         default_range(L,U).
&sus{price(P) : selected(P)} =: price(total).

#show selected/1.
&show{price/1}.
```

Here, we assign selected parts that are missing the price information a default within a certain range. 
Calling 

```
flingo examples/config_default_in.lp 0
```
results in
```
Answer: 1
selected(frame) val(price(total),15) val(price(frame),15)
Answer: 2
selected(frame) selected(bag) val(price(total),16) val(price(frame),15) val(price(bag),1)
Answer: 3
selected(frame) selected(bag) val(price(total),17) val(price(frame),15) val(price(bag),2)
```
were in answers 2 and 3, the two possible defaults for the missing price information of the selected bag is used.

### 4. Defined

The atom in 4. may be used in the body to reason about whether a given variable `x` is defined or not. This is useful for instance to provide defaults or detect errors if a certain integer variable does not have a value but should.

For instance, program
```
price(frame,15).

default_price(20).

  selected(frame).
{ selected(bag) }.

&sus{V} = price(P)    :- selected(P), price(P,V).
&sus{price(P) : selected(P)} =: calc_price(total).

&sus{price(total)} = calc_price(total) :- &df{calc_price(total)}.
&sus{price(total)} = D                 :- not &df{calc_price(total)},
                                          default_price(D).

#show selected/1.
&show{price/1}.
```
first tries to calculate the price, and if this calculation has a defined outcome, it is assigned to the total price. If not, a default price is used.

Calling
```
flingo examples/config_default_in.lp 0
```
yields the intended two answer sets
```
Answer: 1
selected(frame) selected(bag) val(price(frame),15) val(price(total),20)
Answer: 2
selected(frame) val(price(frame),15) val(price(total),15)
```
where Answer 1 makes use of the default because the price of the bag is missing and therefore the total price may not be calculated.

### 5./6. Minimum and maximum aggregates

Atoms in 5. and 6. determine the minimum and maximum among linear terms in the set that have a defined value, respectively. They may be used in the head as well as in the body.

```
price(frame,15). part(frame).
price(bag,5).      part(bag).

  selected(frame).
{ selected(bag) }.

&sus{V} = price(P) :- selected(P), price(P,V).
&sus{price(P) : selected(P)} = price(total).

min_price(P) :- &min{price(P') : selected(P')} = price(P),
                part(P).
max_price(P) :- &max{price(P') : selected(P')} = price(P),
                part(P).

#show selected/1.
#show min_price/1.
#show max_price/1.
&show{price/1}.
```
Here, atoms `min_price/1` and `max_price/1` query what selected part has the minimum and the maximum value, respectively. 

The call
```
flingo config_minmax_price.lp 0
```
yields
```
Answer: 1
selected(frame) min_price(frame) max_price(frame) val(price(total),15) val(price(frame),15)
Answer: 2
selected(frame) selected(bag) min_price(bag) max_price(frame) val(price(total),20) val(price(frame),15) val(price(bag),5)
```
When the bag is not selected, the frame has the minimum and maximum price. In the second answer, we see that the bag has the minimum price among selected parts, while the frame's price is the maximum.

### Choices
Similarly to the language of clingo, flingo allows for choice rules in the head of a rule. Choices have the following form:
```
&fun{ lt1 :: ca1 : c1;...ltn :: can : cn} <> lt0
```
where `fun` is either `sum`, `sus`, `min`, or `max`,
`lti` are linear terms, `cai` are regular atoms that may be chosen, and
`ci` are conjunctions of literals for `i` between 0 and `n`,
and `<>` is either `<=`,`=`,`!=`,`<`,`>`, or `>=`.

As an example program
```
part(sportsframe).    price(sportsframe,15).   type(sportsframe,frame).
part(standardframe).  price(standardframe,14). type(standardframe,frame).
part(fancysaddle).    price(fancysaddle,6).    type(fancysaddle,saddle). 
part(standardsaddle). price(standardsaddle,5). type(standardsaddle,saddle). 

&sum{V} = price(P) :- price(P,V).

pricelimit(20).

&sum{price(P) :: selected(P) : part(P)} <= X :- pricelimit(X).
:- selected(P), selected(P'), P<P', 
   type(P,T),   type(P',T).
:- type(_,T), { selected(P) : type(P,T) }0.

#show selected/1.
&show{}.
```
Our parts database for the bike is now more involved. Each part has a price and a type. It contains two choices for the frame, either standard or sports, and two choices for the saddle, either standard or fancy. As before, we store the prices in integer variables and we have a price limit. 

Using a choice, we can now express in one line, that we may freely select parts such that the price limit is respected. We further restrict solutions such that every type has something selected and there is only one option per type selected.

Calling
```
flingo examples/config_pricelimit_choice.lp 0
```
outputs the three possible answers
```
Answer: 1
selected(standardframe) selected(fancysaddle)
Answer: 2
selected(standardframe) selected(standardsaddle)
Answer: 3
selected(sportsframe) selected(standardsaddle)
```
One has enough money to either combine the standard frame with the fancy saddle or the standard one, but if one opts for the sportsframe, the only viable choice is the standard saddle.

For another example, we replace from the program above the choice rule and the price limit with
```
maxlimit(14).

&max{price(P) :: selected(P) : part(P)} <= X :- maxlimit(X).
```
Now we restrict the maximum price an individual part may have.

Calling
```
flingo examples/config_pricelimit_choice.lp 0
```
gives us
```
Answer: 1
selected(standardframe) selected(standardsaddle)
Answer: 2
selected(standardframe) selected(fancysaddle)
```
The new program removes all combinations using the sports frame since this part violates the maximum allowed spending for one part.

## Development

To install the development version of `flingo`
```bash
pip install -e .
```

To improve code quality, we run linters, and unit tests. The
tools can be run using [nox]. We recommend installing nox using [pipx] to have
it available globally:

```bash
python -m pip install pipx
python -m pipx install nox
nox
```

Note that `nox --no-install -r` can be used to speed up subsequent runs. It
avoids recreating virtual environments. For example, to run the unit tests
without recreating the corresponding environment and installing packages each
time, you can use

```bash
nox --no-install -rs test
```
There is also a format session for nox. It can be run as follows:

```bash
nox -rs format
nox -rs format -- check
```

The latter command can be used to inspect changes before applying them.

[doc]: https://potassco.org/clingo/python-api/current/
[nox]: https://nox.thea.codes/en/stable/index.html
[pipx]: https://pypa.github.io/pipx/
