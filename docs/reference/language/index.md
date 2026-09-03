---
icon: "material/pen-plus"
---

# Flingo Language

## Language Constructs

flingo atoms have the following forms, explore the links below for details on each construct.

- [Sum under clingo semantics][sum-clingo]
```clingo
&sum{lt1 : c1;...;ltn : cn} <> l0
```
- [Sum under strict semantics][sum-strict]
```clingo
&sus{lt1 : c1;...;ltn : cn} <> l0
```
- [Assignments][assignments]
```clingo
&in{lb..ub} =: x
```
- [Defined][defined]
```clingo
&df{x}
```
- [Minimum and maximum aggregates][min-max]
```clingo
&min{lt1 : c1;...;ltn : cn} <> l0
&max{lt1 : c1;...;ltn : cn} <> l0
```

!!! note

    - `lti`, `lb`, and `ub` are linear terms.
    - `ci` is a conjunction of literals for `i` between 0 and `n`.
    - `x` is the name of a variable.
    - `<>` is one of `<=`, `=`, `!=`, `<`, `>`, or `>=`.



## Showing assignments

Use the `&show{v1/a1; ...; vn/an}` directive to control which variable
assignments are shown. In this directive, `vi` is the function name and `ai` is
its arity.

!!! example

    ```lp
    &show{x/0; price/1}
    ```

    The term `x/0` shows the variable named `x`, while `price/1` shows all
    variables of the form `price(<argument>)`.

If the directive is absent, all variables are shown. Use `&show{}` to hide all
variables.


## Choices

Similarly to the language of clingo, flingo allows for choice rules in the head of a rule. Choices have the following form:
```
&fun{ lt1 :: ca1 : c1;...ltn :: can : cn} <> lt0
```
where `fun` is either `sum`, `sus`, `min`, or `max`,
`lti` are linear terms, `cai` are regular atoms that may be chosen, and
`ci` are conjunctions of literals for `i` between 0 and `n`,
and `<>` is either `<=`,`=`,`!=`,`<`,`>`, or `>=`.

!!! example

      As an example program
      ```clingo
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

[sum-clingo]: sum.md
[sum-strict]: sus.md
[assignments]: in.md
[defined]: def.md
[min-max]: minmax.md

