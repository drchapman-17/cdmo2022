include "globals.mzn";
include "chuffed.mzn";

% --------------------------- CONFIGs ---------------------------

% Check the following boxes in the solver configuration:
  % SOLVER  -> Chuffed;
  % SOLVING -> Free search;
  % OUTPUT  -> Output solving statistics;

% Toy case
w_c = [3,2,2,3,4];
h_c = [3,4,8,9,12];
n = 5;
w = 9;

% -------------------------- VARIABLES --------------------------

int: w;                               % Width of the silicon plate
int: n;                               % Number of components

array[1..n] of int: w_c;              % Width of components
array[1..n] of int: h_c;              % Height of components
array[1..n] of var int: area;         % Areas of components

int: max_h = sum(h_c[1..n]);              % Height of the silicon plate 

array[1..n] of var 1..max(w,max_h): x;    % x dimensions of components
array[1..n] of var 1..max(w,max_h): y;    % y dimensions of components

% Variable to minimize
var int: h = max([y[i] + h_c[i] | i in 1..n]); 

% ------------------------- CONSTRAINTS -------------------------

% CONSTRAINT 1.1
% Areas definition constraint
constraint 
  forall (i in 1..n)
    (area[i] = w_c[i] * h_c[i]);

% CONSTRAINT 1.2
% Each circuits inside the silicon plate
constraint 
  forall (i in 1..n) 
    (x[i] <= w - w_c[i] + 1);

% CONSTRAINT 1.3
% No overlap 
constraint 
  diffn (x[1..n], y[1..n], w_c[1..n], h_c[1..n]) :: domain;


% ----------------- SIMMETRY BREAKING CONSTRAINTS ----------------- 

% CONSTRAINT 2.1
% break simmetry constraint: pos[i,1] <= w-pos[i,1]-dim[i,1]+1
var int: i_max = arg_max(area); 

constraint 
  2 * x[i_max] <= w - w_c[i_max] + 1;
constraint 
  2 * y[i_max] <= h - h_c[i_max] + 1;

% CONSTRAINT 2.2
% Faster understanding to have found the optimal solution
var int: empty_space= w * h - sum(area);

constraint 
  empty_space >= 0;


% ------------------------------ SEARCH ------------------------------
ann: search_ann = priority_search(area, 
      [int_search([y[i],x[i]], input_order, indomain_min) | i in 1..n],largest, complete);

solve :: search_ann minimize h;

output
  ["[[\(w), \(h)],\n"] ++ 
  ["[\(w_c[i]), \(h_c[i]), \(x[i]), \(y[i])],\n" | i in 1..n-1] ++
  ["[\(w_c[n]), \(h_c[n]), \(x[n]), \(y[n])]]"]