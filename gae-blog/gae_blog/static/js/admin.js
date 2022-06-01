const deleteModal = new bootstrap.Modal(document.getElementById("confirmDelete"), {});

// Handles marking table rows for delete for tables that support row delete
document.querySelectorAll(".delete_rows_table tbody tr").forEach(function(element, index) {
  element.onclick = toggleDelete;
});


// Adds/Removes the delete class from a table row
function toggleDelete(e){
    if (e.target.parentNode.tagName == "TR"){
        e.preventDefault();
        const parentElem = e.target.parentNode;
        parentElem.classList.toggle('for-delete');
        //parentElem.classList.toggle('row-disabled');
        toggleDisableDelete()
    }
}


// If lines are marked for delete, then enable the delete button
// else disable it
function toggleDisableDelete(){
    if (document.querySelectorAll(".delete_rows_table tbody tr.for-delete").length > 0)
        document.getElementById("postsDelete").classList.remove("icon-disabled")
    else
        document.getElementById("postsDelete").classList.add("icon-disabled")
}

// Display a confirmation popup when user clicks the delete icon
document.getElementById("postsDelete").onclick = function(e){
    deleteModal.show();
    
};

// User has confirmed they want to delete selected rows in the table
document.getElementById("btnConfirmDelete").onclick = function(e){
    deleteRows();
};


// Make the call to delete the rows
function deleteRows(){
    const rows4Delete = [];
    document.querySelectorAll(".delete_rows_table tbody tr.for-delete").forEach(function(element, index) {
        rows4Delete.push( element.id );
    })


    fetch("/admin/post/delete/", {
      method: "post",
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },

      //Make sure to serialize your JSON body
      body: JSON.stringify({
        objectIds: rows4Delete.toString()
      })
    })
    .then(response => response.json())
    .then(data => {
        deleteModal.hide();
        if(data.delete_status == "ERROR")
            alert("There was an error while deleting posts. Check the logs.")
        else{
            // Reload the page so that the deleted rows are no longer visible
            location.reload();
        }
    })

    


}