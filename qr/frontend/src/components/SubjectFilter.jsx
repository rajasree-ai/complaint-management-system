import React from "react";

function SubjectFilter({
subject,
setSubject
}) {

return (

<select

value={subject}

onChange={(e)=>
setSubject(
e.target.value
)
}
>

<option value="">
All Subjects
</option>

<option value="Maths">
Maths
</option>

<option value="Physics">
Physics
</option>

<option value="Python">
Python
</option>

<option value="AI">
AI
</option>

</select>

);

}

export default SubjectFilter;