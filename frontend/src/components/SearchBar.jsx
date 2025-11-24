import React from 'react';

export const SearchBar = ({ value, onChange, onSubmit, loading = false }) => {
  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(e);
  };

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-2xl mx-auto">
      <div className="relative">
        <input
          type="text"
          placeholder="Busque por título, autor ou categoria..."
          value={value}
          onChange={(e) => onChange(e.target.value)}
          disabled={loading}
          className="search-bar-input"
        />
        <button
          type="submit"
          disabled={loading}
          className="search-bar-button"
        >
          {loading ? '⏳' : '🔍'}
        </button>
      </div>
    </form>
  );
};