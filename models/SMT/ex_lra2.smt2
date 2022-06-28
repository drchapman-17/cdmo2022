(set-logic QF_LIRA)
;(set-option :produce-models true)
;(set-option :incremental true)
(declare-fun x () Real)
(declare-fun y () Real)
(declare-fun h () Real)
(declare-fun w () Real)
(push 1)

(assert (or (not A) (>= (+ (* 2 x) y) (- 2))))
(assert (or A (>= (- (* 4 x) y) (- 4))))
(check-sat)
(get-model)

(pop 1)
(declare-fun A () Int)

(assert (or (< A 0) (>= (- (* 4 x) y) (- 4))))
(assert (or (>= A 0) (< (- (* 2 x) y) (- 6))))

(check-sat)
(get-model)
