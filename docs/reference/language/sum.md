# Sum under clingo semantics

```clingo
&sum{lt1 : c1;...;ltn : cn} <> l0
```

This atom sums up all linear terms in the set. It can be seen as a generalization of clingo sum aggregates as it similarly removes undefined elements, and therefore always returns a value. It can be used in the head and in the body.

!!! example

    ```clingo
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

    ```clingo
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
