#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <ctype.h>
#include <stdbool.h>

#define MAX_ALIMENTE 100
#define MAX_INGREDIENTE 50
#define MAX_CZA_ENTRIES 100
#define MAX_LINE_LENGTH 256
#define DATA_DIR "../data"
#define RETETAR_FILE DATA_DIR "/retetar.json"
#define CZA_FILE DATA_DIR "/cza.json"

typedef struct {
    char id[37]; // UUID length
    char nume[100];
    char um[20];
    float cantitate;
} Ingredient;

typedef struct {
    char nume[100];
    Ingredient ingrediente[MAX_INGREDIENTE];
    int num_ingrediente;
} Aliment;

typedef struct {
    char ingredient[100];
    char um[20];
    float cantitate_pp; // per persoană
    float cantitate_totala;
} CZAIngredient;

typedef struct {
    char aliment[100];
    int nr_persoane;
    CZAIngredient ingrediente[MAX_INGREDIENTE];
    int num_ingrediente;
} CZAEntry;

typedef struct {
    char loc_consum[10];
    char masa_zi[10];
    char regim_alimentar[10];
    char data[11]; // dd.mm.yyyy
    CZAEntry entries[MAX_CZA_ENTRIES];
    int num_entries;
} CZALocConsum;

// Global state
Aliment retetar[MAX_ALIMENTE];
int num_alimente = 0;

CZALocConsum cza_data[MAX_CZA_ENTRIES];
int num_cza_entries = 0;

typedef struct {
    int persoane_c1;
    int persoane_c2;
    int persoane_c3;
    char masa_zi[10];
    char regim_alimentar[10];
    char data[11];
} SelectedCoordinates;

SelectedCoordinates current_coords = {0, 0, 0, "M1", "R1", ""};

// Utility functions
void create_data_dir() {
    #ifdef _WIN32
    system("mkdir ..\\data 2> nul");
    #else
    system("mkdir -p ../data");
    #endif
}

void generate_uuid(char *uuid_str) {
    // Simplified UUID generation for this example
    const char *chars = "0123456789abcdef";
    for (int i = 0; i < 36; i++) {
        if (i == 8 || i == 13 || i == 18 || i == 23) {
            uuid_str[i] = '-';
        } else {
            uuid_str[i] = chars[rand() % 16];
        }
    }
    uuid_str[36] = '\0';
}

void get_current_date(char *date_str) {
    time_t t = time(NULL);
    struct tm tm = *localtime(&t);
    sprintf(date_str, "%02d.%02d.%04d", tm.tm_mday, tm.tm_mon + 1, tm.tm_year + 1900);
}

// JSON parsing/writing (simplified for this example)
void write_retetar_to_file() {
    FILE *f = fopen(RETETAR_FILE, "w");
    if (!f) return;
    
    fprintf(f, "{\n");
    for (int i = 0; i < num_alimente; i++) {
        fprintf(f, "  \"%s\": {\n", retetar[i].nume);
        for (int j = 0; j < retetar[i].num_ingrediente; j++) {
            fprintf(f, "    \"%s\": {\n", retetar[i].ingrediente[j].id);
            fprintf(f, "      \"ingredient\": \"%s\",\n", retetar[i].ingrediente[j].nume);
            fprintf(f, "      \"um\": \"%s\",\n", retetar[i].ingrediente[j].um);
            fprintf(f, "      \"cantitate\": %.2f\n", retetar[i].ingrediente[j].cantitate);
            fprintf(f, "    }%s\n", (j == retetar[i].num_ingrediente - 1) ? "" : ",");
        }
        fprintf(f, "  }%s\n", (i == num_alimente - 1) ? "" : ",");
    }
    fprintf(f, "}\n");
    fclose(f);
}

void load_retetar_from_file() {
    // In a real implementation, you would use a proper JSON parser
    // This is a simplified version that assumes a specific format
    
    FILE *f = fopen(RETETAR_FILE, "r");
    if (!f) return;
    
    // Reset retetar
    num_alimente = 0;
    
    char line[MAX_LINE_LENGTH];
    char current_aliment[100] = "";
    char current_ingredient_id[37] = "";
    char current_ingredient_name[100] = "";
    char current_um[20] = "";
    float current_cantitate = 0;
    
    while (fgets(line, sizeof(line), f)) {
        // Remove newline
        line[strcspn(line, "\n")] = 0;
        
        // Check for aliment
        if (strstr(line, "\":")) {
            char *start = strchr(line, '"') + 1;
            char *end = strchr(start + 1, '"');
            *end = '\0';
            strcpy(current_aliment, start);
            
            // Add new aliment
            strcpy(retetar[num_alimente].nume, current_aliment);
            retetar[num_alimente].num_ingrediente = 0;
            num_alimente++;
        }
        // Check for ingredient id
        else if (strstr(line, "\": {")) {
            char *start = strchr(line, '"') + 1;
            char *end = strchr(start + 1, '"');
            *end = '\0';
            strcpy(current_ingredient_id, start);
        }
        // Check for ingredient name
        else if (strstr(line, "\"ingredient\":")) {
            char *start = strstr(line, "\"ingredient\": \"") + 14;
            char *end = strchr(start, '"');
            *end = '\0';
            strcpy(current_ingredient_name, start);
        }
        // Check for um
        else if (strstr(line, "\"um\":")) {
            char *start = strstr(line, "\"um\": \"") + 7;
            char *end = strchr(start, '"');
            *end = '\0';
            strcpy(current_um, start);
        }
        // Check for cantitate
        else if (strstr(line, "\"cantitate\":")) {
            char *start = strstr(line, "\"cantitate\": ") + 12;
            current_cantitate = atof(start);
            
            // Add the ingredient to the current aliment
            if (num_alimente > 0 && current_aliment[0] && current_ingredient_id[0]) {
                Aliment *a = &retetar[num_alimente - 1];
                if (a->num_ingrediente < MAX_INGREDIENTE) {
                    strcpy(a->ingrediente[a->num_ingrediente].id, current_ingredient_id);
                    strcpy(a->ingrediente[a->num_ingrediente].nume, current_ingredient_name);
                    strcpy(a->ingrediente[a->num_ingrediente].um, current_um);
                    a->ingrediente[a->num_ingrediente].cantitate = current_cantitate;
                    a->num_ingrediente++;
                }
            }
        }
    }
    
    fclose(f);
}

// CZA functions
void write_cza_to_file() {
    FILE *f = fopen(CZA_FILE, "w");
    if (!f) return;
    
    fprintf(f, "{\n");
    for (int i = 0; i < num_cza_entries; i++) {
        CZALocConsum *loc = &cza_data[i];
        fprintf(f, "  \"%s_%s_%s_%s\": {\n", loc->loc_consum, loc->masa_zi, loc->regim_alimentar, loc->data);
        
        for (int j = 0; j < loc->num_entries; j++) {
            CZAEntry *entry = &loc->entries[j];
            fprintf(f, "    \"%s\": {\n", entry->aliment);
            fprintf(f, "      \"nr_persoane\": %d,\n", entry->nr_persoane);
            fprintf(f, "      \"ingrediente\": [\n");
            
            for (int k = 0; k < entry->num_ingrediente; k++) {
                CZAIngredient *ing = &entry->ingrediente[k];
                fprintf(f, "        {\n");
                fprintf(f, "          \"id\": \"%d\",\n", k);
                fprintf(f, "          \"ingredient\": \"%s\",\n", ing->ingredient);
                fprintf(f, "          \"um\": \"%s\",\n", ing->um);
                fprintf(f, "          \"cantitate_per_persoana\": %.2f,\n", ing->cantitate_pp);
                fprintf(f, "          \"cantitate_totala\": %.2f\n", ing->cantitate_totala);
                fprintf(f, "        }%s\n", (k == entry->num_ingrediente - 1) ? "" : ",");
            }
            
            fprintf(f, "      ]\n");
            fprintf(f, "    }%s\n", (j == loc->num_entries - 1) ? "" : ",");
        }
        
        fprintf(f, "  }%s\n", (i == num_cza_entries - 1) ? "" : ",");
    }
    fprintf(f, "}\n");
    fclose(f);
}

void load_cza_from_file() {
    // Similar to load_retetar_from_file but for CZA data
    // Implementation omitted for brevity
}

// Menu functions
void show_retetar_menu() {
    printf("\n=== RETETAR ===\n");
    printf("1. Afiseaza alimente\n");
    printf("2. Adauga aliment nou\n");
    printf("3. Editeaza aliment\n");
    printf("4. Sterge aliment\n");
    printf("5. Adauga ingredient\n");
    printf("6. Editeaza ingredient\n");
    printf("7. Sterge ingredient\n");
    printf("0. Inapoi\n");
    printf("Alegere: ");
}

void show_cza_menu() {
    printf("\n=== CZA ===\n");
    printf("1. Seteaza coordonate\n");
    printf("2. Adauga aliment in CZA\n");
    printf("3. Afiseaza CZA curent\n");
    printf("4. Genereaza lista alimente\n");
    printf("0. Inapoi\n");
    printf("Alegere: ");
}

void display_alimente() {
    printf("\n=== ALIMENTE ===\n");
    for (int i = 0; i < num_alimente; i++) {
        printf("%d. %s (%d ingrediente)\n", i+1, retetar[i].nume, retetar[i].num_ingrediente);
    }
}

void display_aliment_details(int index) {
    if (index < 0 || index >= num_alimente) return;
    
    printf("\n=== %s ===\n", retetar[index].nume);
    printf("Ingrediente:\n");
    for (int i = 0; i < retetar[index].num_ingrediente; i++) {
        printf("%d. %s - %.2f %s\n", i+1, 
               retetar[index].ingrediente[i].nume,
               retetar[index].ingrediente[i].cantitate,
               retetar[index].ingrediente[i].um);
    }
}

void add_aliment() {
    if (num_alimente >= MAX_ALIMENTE) {
        printf("Numar maxim de alimente atins!\n");
        return;
    }
    
    char nume[100];
    printf("Nume aliment: ");
    fgets(nume, sizeof(nume), stdin);
    nume[strcspn(nume, "\n")] = 0;
    
    // Check if already exists
    for (int i = 0; i < num_alimente; i++) {
        if (strcmp(retetar[i].nume, nume) == 0) {
            printf("Alimentul exista deja!\n");
            return;
        }
    }
    
    strcpy(retetar[num_alimente].nume, nume);
    retetar[num_alimente].num_ingrediente = 0;
    num_alimente++;
    
    write_retetar_to_file();
    printf("Aliment adaugat cu succes!\n");
}

void set_coordinates() {
    printf("\n=== SETEAZA COORDONATE ===\n");
    
    printf("Persoane C1 (0-127): ");
    scanf("%d", &current_coords.persoane_c1);
    getchar(); // Consume newline
    
    printf("Persoane C2 (0-127): ");
    scanf("%d", &current_coords.persoane_c2);
    getchar();
    
    printf("Persoane C3 (0-127): ");
    scanf("%d", &current_coords.persoane_c3);
    getchar();
    
    printf("Masa din zi (M1-M5): ");
    fgets(current_coords.masa_zi, sizeof(current_coords.masa_zi), stdin);
    current_coords.masa_zi[strcspn(current_coords.masa_zi, "\n")] = 0;
    
    printf("Regim alimentar (R1-R6): ");
    fgets(current_coords.regim_alimentar, sizeof(current_coords.regim_alimentar), stdin);
    current_coords.regim_alimentar[strcspn(current_coords.regim_alimentar, "\n")] = 0;
    
    printf("Data (dd.mm.yyyy) [enter pentru data curenta]: ");
    char date_input[11];
    fgets(date_input, sizeof(date_input), stdin);
    date_input[strcspn(date_input, "\n")] = 0;
    
    if (strlen(date_input)) {
        strcpy(current_coords.data, date_input);
    } else {
        get_current_date(current_coords.data);
    }
    
    printf("Coordonate setate: C1(%d) C2(%d) C3(%d) %s %s %s\n",
           current_coords.persoane_c1, current_coords.persoane_c2, current_coords.persoane_c3,
           current_coords.masa_zi, current_coords.regim_alimentar, current_coords.data);
}

void add_aliment_to_cza() {
    if (num_alimente == 0) {
        printf("Nu exista alimente in retetar!\n");
        return;
    }
    
    if (current_coords.persoane_c1 == 0 && 
        current_coords.persoane_c2 == 0 && 
        current_coords.persoane_c3 == 0) {
        printf("Nu exista persoane in niciun loc de consum!\n");
        return;
    }
    
    display_alimente();
    printf("Selecteaza aliment (1-%d): ", num_alimente);
    int choice;
    scanf("%d", &choice);
    getchar(); // Consume newline
    
    if (choice < 1 || choice > num_alimente) {
        printf("Selectie invalida!\n");
        return;
    }
    
    Aliment *selected = &retetar[choice-1];
    
    // Add to CZA for each active location
    if (current_coords.persoane_c1 > 0) {
        add_aliment_to_cza_loc("C1", current_coords.persoane_c1, selected);
    }
    if (current_coords.persoane_c2 > 0) {
        add_aliment_to_cza_loc("C2", current_coords.persoane_c2, selected);
    }
    if (current_coords.persoane_c3 > 0) {
        add_aliment_to_cza_loc("C3", current_coords.persoane_c3, selected);
    }
    
    write_cza_to_file();
    printf("Aliment adaugat in CZA cu succes!\n");
}

void add_aliment_to_cza_loc(const char *loc_consum, int nr_persoane, Aliment *aliment) {
    // Find or create CZA entry for these coordinates
    char key[100];
    sprintf(key, "%s_%s_%s_%s", loc_consum, current_coords.masa_zi, 
            current_coords.regim_alimentar, current_coords.data);
    
    CZALocConsum *loc = NULL;
    for (int i = 0; i < num_cza_entries; i++) {
        char current_key[100];
        sprintf(current_key, "%s_%s_%s_%s", cza_data[i].loc_consum, cza_data[i].masa_zi,
                cza_data[i].regim_alimentar, cza_data[i].data);
        
        if (strcmp(current_key, key) == 0) {
            loc = &cza_data[i];
            break;
        }
    }
    
    if (!loc) {
        if (num_cza_entries >= MAX_CZA_ENTRIES) {
            printf("Numar maxim de intrari CZA atins!\n");
            return;
        }
        
        loc = &cza_data[num_cza_entries++];
        strcpy(loc->loc_consum, loc_consum);
        strcpy(loc->masa_zi, current_coords.masa_zi);
        strcpy(loc->regim_alimentar, current_coords.regim_alimentar);
        strcpy(loc->data, current_coords.data);
        loc->num_entries = 0;
    }
    
    // Check if aliment already exists in this CZA entry
    for (int i = 0; i < loc->num_entries; i++) {
        if (strcmp(loc->entries[i].aliment, aliment->nume) == 0) {
            printf("Alimentul exista deja in CZA pentru aceste coordonate!\n");
            return;
        }
    }
    
    if (loc->num_entries >= MAX_CZA_ENTRIES) {
        printf("Numar maxim de alimente in CZA atins!\n");
        return;
    }
    
    CZAEntry *entry = &loc->entries[loc->num_entries++];
    strcpy(entry->aliment, aliment->nume);
    entry->nr_persoane = nr_persoane;
    entry->num_ingrediente = 0;
    
    // Add all ingredients
    for (int i = 0; i < aliment->num_ingrediente; i++) {
        if (entry->num_ingrediente >= MAX_INGREDIENTE) break;
        
        CZAIngredient *ing = &entry->ingrediente[entry->num_ingrediente++];
        strcpy(ing->ingredient, aliment->ingrediente[i].nume);
        strcpy(ing->um, aliment->ingrediente[i].um);
        ing->cantitate_pp = aliment->ingrediente[i].cantitate;
        ing->cantitate_totala = aliment->ingrediente[i].cantitate * nr_persoane;
    }
}

void display_current_cza() {
    printf("\n=== CZA CURENT ===\n");
    printf("Coordonate: C1(%d) C2(%d) C3(%d) %s %s %s\n",
           current_coords.persoane_c1, current_coords.persoane_c2, current_coords.persoane_c3,
           current_coords.masa_zi, current_coords.regim_alimentar, current_coords.data);
    
    bool found = false;
    
    for (int i = 0; i < num_cza_entries; i++) {
        CZALocConsum *loc = &cza_data[i];
        
        // Check if this entry matches our current coordinates
        bool matches = false;
        if (current_coords.persoane_c1 > 0 && strcmp(loc->loc_consum, "C1") == 0) matches = true;
        if (current_coords.persoane_c2 > 0 && strcmp(loc->loc_consum, "C2") == 0) matches = true;
        if (current_coords.persoane_c3 > 0 && strcmp(loc->loc_consum, "C3") == 0) matches = true;
        
        if (!matches) continue;
        if (strcmp(loc->masa_zi, current_coords.masa_zi) != 0) continue;
        if (strcmp(loc->regim_alimentar, current_coords.regim_alimentar) != 0) continue;
        if (strcmp(loc->data, current_coords.data) != 0) continue;
        
        found = true;
        
        printf("\nLoc de consum: %s\n", loc->loc_consum);
        for (int j = 0; j < loc->num_entries; j++) {
            CZAEntry *entry = &loc->entries[j];
            printf("Aliment: %s (%d persoane)\n", entry->aliment, entry->nr_persoane);
            
            printf("Ingrediente:\n");
            for (int k = 0; k < entry->num_ingrediente; k++) {
                CZAIngredient *ing = &entry->ingrediente[k];
                printf("- %s: %.2f %s (%.2f per persoana)\n", 
                       ing->ingredient, ing->cantitate_totala, ing->um, ing->cantitate_pp);
            }
            printf("\n");
        }
    }
    
    if (!found) {
        printf("Nu exista alimente in CZA pentru coordonatele curente.\n");
    }
}

void generate_food_list() {
    printf("\n=== LISTA ALIMENTE %s ===\n", current_coords.data);
    
    // Aggregate all ingredients for the selected date
    typedef struct {
        char ingredient[100];
        char um[20];
        float cantitate_totala;
    } TotalIngredient;
    
    TotalIngredient totals[MAX_INGREDIENTE * MAX_CZA_ENTRIES];
    int num_totals = 0;
    
    for (int i = 0; i < num_cza_entries; i++) {
        CZALocConsum *loc = &cza_data[i];
        
        // Check if this entry matches our selected date
        if (strcmp(loc->data, current_coords.data) != 0) continue;
        
        for (int j = 0; j < loc->num_entries; j++) {
            CZAEntry *entry = &loc->entries[j];
            
            for (int k = 0; k < entry->num_ingrediente; k++) {
                CZAIngredient *ing = &entry->ingrediente[k];
                
                // Check if we already have this ingredient in totals
                bool found = false;
                for (int t = 0; t < num_totals; t++) {
                    if (strcmp(totals[t].ingredient, ing->ingredient) == 0 && 
                        strcmp(totals[t].um, ing->um) == 0) {
                        totals[t].cantitate_totala += ing->cantitate_totala;
                        found = true;
                        break;
                    }
                }
                
                if (!found) {
                    if (num_totals >= MAX_INGREDIENTE * MAX_CZA_ENTRIES) continue;
                    
                    strcpy(totals[num_totals].ingredient, ing->ingredient);
                    strcpy(totals[num_totals].um, ing->um);
                    totals[num_totals].cantitate_totala = ing->cantitate_totala;
                    num_totals++;
                }
            }
        }
    }
    
    if (num_totals == 0) {
        printf("Nu exista date CZA pentru data selectata.\n");
        return;
    }
    
    // Display the totals
    printf("Ingredient\tUM\tCantitate totala\n");
    printf("----------------------------------------\n");
    for (int i = 0; i < num_totals; i++) {
        printf("%s\t%s\t%.2f\n", totals[i].ingredient, totals[i].um, totals[i].cantitate_totala);
    }
    
    // Option to save to file
    printf("\nSalveaza lista in fisier? (d/n): ");
    char choice;
    scanf("%c", &choice);
    getchar(); // Consume newline
    
    if (tolower(choice) == 'd') {
        char filename[100];
        sprintf(filename, "lista_alimente_%s.txt", current_coords.data);
        
        FILE *f = fopen(filename, "w");
        if (f) {
            fprintf(f, "LISTA ALIMENTE %s\n\n", current_coords.data);
            fprintf(f, "Ingredient\tUM\tCantitate totala\n");
            fprintf(f, "----------------------------------------\n");
            
            for (int i = 0; i < num_totals; i++) {
                fprintf(f, "%s\t%s\t%.2f\n", totals[i].ingredient, totals[i].um, totals[i].cantitate_totala);
            }
            
            fclose(f);
            printf("Lista salvata in %s\n", filename);
        } else {
            printf("Eroare la salvarea fisierului!\n");
        }
    }
}

int main() {
    srand(time(NULL)); // For UUID generation
    
    // Initialize current date
    get_current_date(current_coords.data);
    
    // Create data directory if it doesn't exist
    create_data_dir();
    
    // Load data
    load_retetar_from_file();
    load_cza_from_file();
    
    // Main menu
    while (1) {
        printf("\n=== APLICATIA DIETA ===\n");
        printf("1. Rețetar\n");
        printf("2. CZA\n");
        printf("0. Ieșire\n");
        printf("Alegere: ");
        
        int choice;
        scanf("%d", &choice);
        getchar(); // Consume newline
        
        if (choice == 0) break;
        
        if (choice == 1) {
            // Retetar submenu
            while (1) {
                show_retetar_menu();
                scanf("%d", &choice);
                getchar();
                
                if (choice == 0) break;
                
                switch (choice) {
                    case 1: // Afiseaza alimente
                        display_alimente();
                        break;
                    case 2: // Adauga aliment nou
                        add_aliment();
                        break;
                    // Other cases would be implemented similarly
                    default:
                        printf("Optiune invalida!\n");
                }
            }
        } else if (choice == 2) {
            // CZA submenu
            while (1) {
                show_cza_menu();
                scanf("%d", &choice);
                getchar();
                
                if (choice == 0) break;
                
                switch (choice) {
                    case 1: // Seteaza coordonate
                        set_coordinates();
                        break;
                    case 2: // Adauga aliment in CZA
                        add_aliment_to_cza();
                        break;
                    case 3: // Afiseaza CZA curent
                        display_current_cza();
                        break;
                    case 4: // Genereaza lista alimente
                        generate_food_list();
                        break;
                    default:
                        printf("Optiune invalida!\n");
                }
            }
        } else {
            printf("Optiune invalida!\n");
        }
    }
    
    return 0;
}
