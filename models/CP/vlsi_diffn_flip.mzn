include "globals.mzn";
include "chuffed.mzn";

-------------------- VARIABLES --------------------

int: w;                                             % width of the silicon plate
int: n;                                             % number of circuits
array[1..n,1..2] of int: dim;                       % original dimensions of circuits
array[1..n] of var bool: flip;                      % flipping or not the circuits  
array[1..n,1..2] of var 1..max(dim): new_dim;       % dimension of the circuits after flipping
array[1..n,1..2] of var 1..max(w,max_l): pos;       % position of the circuits
var int: l=max([pos[i,2] + dim[i,2] |i in 1..n])-1; % length of the silicon plate
array[1..n] of var int: area;                       % area of the circuits

% definition of area
constraint forall(i in 1..n)(area[i]=dim[i,1]*dim[i,2]);

% definition of dimension after flipping
constraint forall(i in 1..n)(if flip[i] then new_dim[i,1..2]=dim[i,1..2] else (new_dim[i,1]=dim[i,2] /\ new_dim[i,2]=dim[i,1]) endif):: domain;

-------------------- CONSTRAINTS --------------------

% if a circuit is a square do not flip it
constraint forall(i in 1..n)(if dim[i,1]=dim[i,2] then flip[i]=0 endif):: domain;

% upper bound for l
int: max_l=sum(dim[1..n,2]);

% lower bound for l
constraint w*l-sum(area)>=0;

% boundary constraints
constraint forall (i in 1..n) (pos[i,1]<=w-new_dim[i,1]+1);

% no-overlapping global constraints 
constraint diffn (pos[1..n,1],pos[1..n,2],new_dim[1..n,1],new_dim[1..n,2]) :: domain;

% cumulative constraints (implied) 
constraint cumulative(pos[1..n,2], new_dim[1..n,2], new_dim[1..n,1], w) :: domain;
constraint cumulative(pos[1..n,1], new_dim[1..n,1], new_dim[1..n,2], l) :: domain;

% break simmetry constraint: the largest circuit in the bottom-left quarter of the plate
% pos[i,1] <= w-pos[i,1]-new_dim[i,1]+1
var int: i_max = arg_max(area); 
constraint 2*pos[i_max,1] <= w-new_dim[i_max,1]+2;
constraint 2*pos[i_max,2] <= l-new_dim[i_max,2]+2;

-------------------- SOLVING --------------------

% annotaion
ann: search_ann;
search_ann = priority_search(area,  [int_search([pos[i,2],pos[i,1]], input_order, indomain_min)| i in 1..n],largest, complete);

% solving
solve :: search_ann minimize l;

% outputting
output["[[\(w), \(l)],\n"]++["[\(dim[i,1]), \(dim[i,2]), \(pos[i,1]), \(pos[i,2])],\n" | i in 1..n-1]++["[\(dim[n,1]), \(dim[n,2]), \(pos[n,1]), \(pos[n,2])]]"]
