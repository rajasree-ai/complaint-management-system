import React from "react";
import MaterialCard
from "./MaterialCard";

function MaterialGrid({
materials
}) {

return (

<div
className="grid"
>

{
materials.map(
(item)=>(
<MaterialCard
key={item._id}
material={item}
/>
))
}

</div>

);

}

export default MaterialGrid;