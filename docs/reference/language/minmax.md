# Minimum and maximum aggregates

```clingo
&min{lt1 : c1;...;ltn : cn} <> l0
&max{lt1 : c1;...;ltn : cn} <> l0
```

These atoms determine the minimum and maximum among linear terms in the set that have a defined value, respectively. They may be used in the head as well as in the body.

!!! example

    For instance, take program


    ```clingo
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

    Execution
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
