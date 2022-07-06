include "globals.mzn";
include "chuffed.mzn";

-------------------- VARIABLES --------------------

int: w; % width of the silicon plate
int: n; % number of circuits
array[1..n,1..2] of int: dim; % dimensions of circuits
array[1..n] of var int: area; % area of the circuits
var int: l=max([pos[i,2]+new_dim[i,2]|i in 1..n])-1; % length of the silicon plate
array[1..n] of var int: diag; % area of the circuits

% definition of area
constraint forall(i in 1..n)(area[i]=dim[i,1]*dim[i,2]);

int: max_l=sum(dim[1..n,2]);
array[1..n,1..2] of var 1..max(w,max_l): pos;

array[1..n] of var bool: flip;
array[1..n,1..2] of var 1..max(dim): new_dim;

constraint forall(i in 1..n)(if flip[i] then new_dim[i,1..2]=dim[i,1..2] else (new_dim[i,1]=dim[i,2] /\ new_dim[i,2]=dim[i,1]) endif):: domain;



% if a circuit is a square do not flip it
constraint forall(i in 1..n)(if dim[i,1]=dim[i,2] then flip[i]=0 endif):: domain;

% each circuit inside the silicon plate
constraint forall (i in 1..n) (pos[i,1]<=w-new_dim[i,1]+1)::domain;

% no overlap between the circuits
constraint diffn (pos[1..n,1],pos[1..n,2],new_dim[1..n,1],new_dim[1..n,2])::domain;

% redundant constraints 
constraint cumulative(pos[1..n,2], new_dim[1..n,2], new_dim[1..n,1], w);
constraint cumulative(pos[1..n,1], new_dim[1..n,1], new_dim[1..n,2], l);

%break simmetry constraint: pos[i,1] <= w-pos[i,1]-dim[i,1]+1
var int: i_max = arg_max(area); 
constraint 2*pos[i_max,1] <= w-new_dim[i_max,1]+1;
constraint 2*pos[i_max,2] <= l-new_dim[i_max,2]+1;

% faster understanding to have found the optimal solution
var int: empty_space=w*l-sum(area);
constraint empty_space>=0;

ann: ann_search;

ann: ann_search_1;
ann_search_1 = priority_search(area,  [int_search([pos[i,2],pos[i,1]], input_order, indomain_min)| i in 1..n], largest, complete);

%ann_search = priority_search(diag,  [int_search([diag[i],pos[i,2]], most_constrained, indomain_min)| i in 1..n],largest, complete);
% case 7 failures = 42877
% case 4 failures = 30072


ann: pos_search;
pos_search = priority_search(area,  [int_search([pos[i,2], pos[i,1]], most_constrained, indomain_min)| i in 1..n], largest, complete);
ann: flip_search;
flip_search = priority_search(diag,  [int_search([flip[i]], input_order, indomain_min)| i in 1..n], largest, complete);
ann_search=seq_search([flip_search, pos_search]);
% case 7 failures = 53576
% case 4 failures = 12504






solve :: ann_search_1 minimize l;

output["[[\(w), \(l)],\n"]++["[\(new_dim[i,1]), \(new_dim[i,2]), \(pos[i,1]), \(pos[i,2])],\n" | i in 1..n-1]++["[\(new_dim[n,1]), \(new_dim[n,2]), \(pos[n,1]), \(pos[n,2])]]"]

