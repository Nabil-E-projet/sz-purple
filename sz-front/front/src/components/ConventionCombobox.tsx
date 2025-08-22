import * as React from "react"
import { Check, ChevronsUpDown, Loader2 } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
} from "@/components/ui/command"
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover"

interface ConventionOption {
  value: string
  label: string
}

interface ConventionComboboxProps {
  value: string
  onChange: (value: string) => void
  placeholder?: string
  className?: string
  conventions: ConventionOption[]
  loading?: boolean
  disabled?: boolean
}

export function ConventionCombobox({ 
  value, 
  onChange, 
  placeholder = "Sélectionner ou saisir une convention...",
  className,
  conventions = [],
  loading = false,
  disabled = false
}: ConventionComboboxProps) {
  const [open, setOpen] = React.useState(false)
  const [inputValue, setInputValue] = React.useState("")
  const [triggerWidth, setTriggerWidth] = React.useState(0)
  const triggerRef = React.useRef<HTMLButtonElement>(null)
  
  // Mesurer la largeur du trigger pour ajuster le popover
  React.useEffect(() => {
    if (triggerRef.current) {
      setTriggerWidth(triggerRef.current.offsetWidth)
    }
  }, [open])
  
  // Filtrer les conventions selon l'entrée utilisateur
  const filteredConventions = conventions.filter((convention) =>
    convention.label.toLowerCase().includes(inputValue.toLowerCase()) ||
    convention.value.toLowerCase().includes(inputValue.toLowerCase())
  )

  // Vérifier si la valeur actuelle correspond à une convention existante
  const selectedConvention = conventions.find((convention) => convention.value === value)
  const displayValue = selectedConvention ? selectedConvention.label : value

  const handleSelect = (currentValue: string) => {
    onChange(currentValue === value ? "" : currentValue)
    setOpen(false)
    setInputValue("")
  }

  const handleCustomValue = () => {
    if (inputValue.trim()) {
      onChange(inputValue.trim())
      setOpen(false)
      setInputValue("")
    }
  }

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          ref={triggerRef}
          variant="outline"
          role="combobox"
          aria-expanded={open}
          disabled={disabled || loading}
          className={cn(
            "w-full justify-between glass-card border-glass-border/30 h-14 text-lg",
            !value && "text-muted-foreground",
            className
          )}
        >
          <span className="truncate text-left">
            {loading ? (
              <span className="flex items-center gap-2">
                <Loader2 className="h-4 w-4 animate-spin" />
                Chargement des conventions...
              </span>
            ) : (
              value ? displayValue : placeholder
            )}
          </span>
          <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent 
        className="p-0 glass-card border-glass-border/30 backdrop-blur-md" 
        style={{ width: triggerWidth || 'auto' }}
        align="start"
        sideOffset={4}
      >
        <Command>
          <CommandInput 
            placeholder="Rechercher une convention..." 
            value={inputValue}
            onValueChange={setInputValue}
            className="h-12"
          />
          <CommandEmpty>
            <div className="py-4 px-4 text-sm text-center">
              {inputValue.trim() ? (
                <div className="space-y-3">
                  <p className="text-muted-foreground">
                    Aucune convention trouvée pour "{inputValue}"
                  </p>
                  <Button 
                    variant="ghost" 
                    size="sm"
                    className="text-primary hover:text-primary/80 font-medium"
                    onClick={handleCustomValue}
                  >
                    Utiliser "{inputValue.trim()}"
                  </Button>
                </div>
              ) : (
                <p className="text-muted-foreground">
                  {loading ? "Chargement..." : "Aucune convention trouvée."}
                </p>
              )}
            </div>
          </CommandEmpty>
          {!loading && (
            <CommandGroup className="max-h-64 overflow-y-auto">
              {filteredConventions.map((convention) => (
                <CommandItem
                  key={convention.value}
                  value={convention.value}
                  onSelect={() => handleSelect(convention.value)}
                  className="cursor-pointer flex items-center gap-2 py-3"
                >
                  <Check
                    className={cn(
                      "h-4 w-4",
                      value === convention.value ? "opacity-100" : "opacity-0"
                    )}
                  />
                  <div className="flex flex-col items-start">
                    <span className="font-medium">{convention.label}</span>
                    {convention.value !== convention.label && (
                      <span className="text-xs text-muted-foreground">{convention.value}</span>
                    )}
                  </div>
                </CommandItem>
              ))}
            </CommandGroup>
          )}
        </Command>
      </PopoverContent>
    </Popover>
  )
}
