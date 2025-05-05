import { useState, useEffect, useRef } from "react";

function SuggestionsInput({ Value, Suggestions, onChange, onSelect }) {

  const [showSuggestions, setShowSuggestions] = useState(false);
  const CellRef = useRef();
  const handleClickOutside = (event) => {
    if (!CellRef.current.contains(event.target)) {
      setShowSuggestions(false);
    }
  };
  useEffect(() => {
    document.addEventListener("click", handleClickOutside);
    return () => {
      document.removeEventListener("click", handleClickOutside);
    };
  });

  return (
    <div ref={CellRef}>
      <input
        type="text"
        value={Value}
        onChange={(event) => {
          setShowSuggestions(true);
          onChange(event);
        }}
      />
      {showSuggestions && Suggestions.length > 0 && (
        <ul className="Drop-list">
          {Suggestions.map((suggestion, index) => (
            <li key={index}
              onClick={() => {
                setShowSuggestions(false);
                onSelect(index)
              }}
            >
              {suggestion}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
export default SuggestionsInput;