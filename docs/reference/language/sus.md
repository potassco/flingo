
# Sum under strict semantics

```clingo
&sus{lt1 : c1;...;ltn : cn} <> l0
```

This atom sums up the linear terms for the conditions that are true. In contrast to `&sum`, if any of the terms is undefined, resulting from an integer variable being undefined that is contained within, the sum is undefined as well. This results in the atom being false. We will later elaborate how this version of sum is useful for assignments later in this document. The atom may be used in the head or in the body.

The example `examples/config_optional.lp` behaves identically when we replace `sus` with `sum`.

Different behavior arises for the price limit.

!!! example

    For instance take program

    ```clingo
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
