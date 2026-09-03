# Assignments

```clingo
&in{lb..ub} =: x
```

This atom is a directional assignment of a value between linear terms `lb` and `ub` to the variable `x`. It may only be used in the head of a rule. Only if `lb` and `ub` are defined, `x` will receive a value in between `lb` and `ub`. Note that this is different from using equality to assign a value. For instance, the fact `&sus{y}=x.` would allow `y` as well as `x` to be defined and take on arbitrary values such that `x` and `y` are equal, while `&in{y..y}=:x.` requires some other rule to define `y` and if that is not the case, `x` remains undefined.
One can also use the strict sum and write `&sus{lt1 : c1;..;ltn : cn}=:x`, where `lti` are linear terms conditioned by conjuctions `ci` for `i` between 1 and `n`, and `x` is an integer variable. Using the strict sum that way has two advantages: first, the strict sum can be undefined in contrast to the clingo sum and thefore `x` only receives a value if the strict sum can be calculated, and second, the linear terms may be conditioned and the arity of the sum can be arbitrary.

!!! example

    For instance, take program

    ```clingo
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
