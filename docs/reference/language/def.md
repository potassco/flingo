# Defined

```clingo
&df{x}
```

This atom may be used in the body to reason about whether a given variable `x` is defined or not. This is useful for instance to provide defaults or detect errors if a certain integer variable does not have a value but should.

!!! example

    For instance, take program


    ```clingo
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
