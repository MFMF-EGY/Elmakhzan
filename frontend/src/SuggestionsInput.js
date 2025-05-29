import { useState, useEffect, useRef } from "react";

function SuggestionsInput({ Value, Suggestions, Disabled, onFocus, onChange, onSelect }) {

  const [showSuggestions, setShowSuggestions] = useState(false);
  const CellRef = useRef();
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (!CellRef.current.contains(event.target)) {
        setShowSuggestions(false);
      }
    };
    
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
        disabled={Disabled}
        onFocus={onFocus}
        onChange={(event) => {
          setShowSuggestions(true);
          onChange(event);
        }}
        onBlur={(event) => {
          if (event.relatedTarget && !CellRef.current.contains(event.relatedTarget)) {
            setShowSuggestions(false);
          }
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