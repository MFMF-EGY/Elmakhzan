import { useState } from "react";

function ItemsListEditor({ ItemsList, setItemsList, ExistingQuantities, SelectedItemIndex, ValidationChecker, setValidationChecker, ItemFieldsStructure }) {
  const addItem = () => {
    let NewItemsList = [...ItemsList];
    NewItemsList.splice(SelectedItemIndex+1 , 0, ItemFieldsStructure);
    NewItemsList.splice(-1, 1);
    let NewValidationChecker = [...ValidationChecker];
    NewValidationChecker.splice(SelectedItemIndex+1, 0, undefined);
    NewValidationChecker.splice(-1, 1);
    setValidationChecker(NewValidationChecker);
    ExistingQuantities.splice(SelectedItemIndex+1, 0, undefined);
    ExistingQuantities.splice(-1, 1);
    setItemsList(NewItemsList);
  };
  const removeItem = () => {
    let NewItemsList = [...ItemsList];
    NewItemsList.splice(SelectedItemIndex, 1);
    NewItemsList.push(ItemFieldsStructure);
    let NewValidationChecker = [...ValidationChecker];
    NewValidationChecker.splice(SelectedItemIndex, 1);
    NewValidationChecker.push(undefined);
    setValidationChecker(NewValidationChecker);
    ExistingQuantities.splice(SelectedItemIndex, 1);
    ExistingQuantities.push(undefined);
    setItemsList(NewItemsList);
  }
  return(
    <ul class="Items-list-editor">
      <button onClick={addItem} disabled={SelectedItemIndex === null}>+</button>
      <button onClick={removeItem} disabled={SelectedItemIndex === null}>x</button>
    </ul>
  )
}
export default ItemsListEditor;