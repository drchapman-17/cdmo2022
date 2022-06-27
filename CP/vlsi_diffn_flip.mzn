include "globals.mzn";
include "chuffed.mzn";

% precision (proportional to w) and number of circuits
% case 1
% dim = [|3, 3|2, 4|2, 8|3, 9|4, 12|]
% n = 5
% w = 9

% case 2
% dim = [|3, 3|2, 8|3, 9|4, 12|4, 4|4, 7|3, 6|8, 10|]
% n = 8
% w = 12

% case 3
% dim = [|7 ,5|15, 4|9 ,12|2, 5|10, 10|13, 2|4, 4|30, 2|]
% n = 8
% w = 30

% case 4
% dim = [|3, 3|2, 4|2, 8|3, 9|4, 12|4, 4|15, 2|4, 7|3, 6|8, 10|]
% n = 10
% w = 15

% case 7
% dim = [|3, 3|3, 4|3, 5|3, 6|3, 7|3, 8|3, 9|5, 4|5, 10|]
% n = 9
% w = 14

% case 10
% n = 12
% w = 17
% dim = [|3, 3|3, 4|3, 5|3, 6|3, 7|3, 8|3, 9|4, 3|4, 8|4 ,14|7, 3|7, 6|]

% case 5
% dim = [|7 ,5|15, 4|9 ,12|2, 5|10, 10|13, 2|4, 4|30, 2|20, 5|5, 7| 18, 12|12, 9|1, 1|5, 11|10, 5| 9, 2| 15, 4|]

% case 37
% n=28
% w=30
% dim = [|5, 7|5 ,14|8 ,14|8 ,4|13 ,21|11, 7|11 ,14|5 ,14|5, 4|3 ,18|3 ,21|11 ,17|11 ,4|4 ,7|4, 5|7, 6|5 ,18|5,3|3, 7|3, 5|4 ,18|4, 3|2 ,12|2, 6|5 ,18|5 ,21|3 ,17|3 ,4 |]

% case 30
% n=27
% w=37
% dim= [|3, 3|3, 4|3, 5|3, 6|3, 7|3, 8|3, 9|3 ,11|3 ,12|3 ,13|3 ,14|3 ,17|3 ,18|3 ,21|4, 3|4, 4|4, 5|4, 6|4 ,10|4 ,22|4 ,24|5, 3|5, 4|5, 6|5 ,10|5 ,14|12 ,37|]

int: w; % width of the silicon plate
int: n; % number of circuits
array[1..n,1..2] of int: dim; % dimensions of circuits
array[1..n] of var int: area; % area of the circuits
array[1..n] of var int: diag; % area of the circuits

constraint forall(i in 1..n)(area[i]=dim[i,1]*dim[i,2]);

constraint forall(i in 1..n)(diag[i]=(dim[i,1]*dim[i,1]+dim[i,2]*dim[i,2]));

int: max_l=sum(dim[1..n,2]);
array[1..n,1..2] of var 1..max(w,max_l): pos;

array[1..n] of var bool: flip;
array[1..n,1..2] of var 1..max(dim): new_dim;

constraint forall(i in 1..n)(if flip[i] then new_dim[i,1..2]=dim[i,1..2] else (new_dim[i,1]=dim[i,2] /\ new_dim[i,2]=dim[i,1]) endif):: domain;

% variable to minimize
var int: l=max([pos[i,2]+new_dim[i,2]|i in 1..n])-1; 

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

